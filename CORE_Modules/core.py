import config
import json
import openai
from AI_Modules.chat import ChatModule
from AI_Modules.prompt import PromptManager
from Memory_Modules.memory import MemoryBuffer
from Utils_Modules import toolslist

class Core:
    def __init__(self, switch):
        """Initialize CORE with Switch, Memory, and Tool Modules."""
        self.switch = switch
        self.chat_module = ChatModule()
        self.memory = MemoryBuffer(buffer_size=10)
        self.tools = self.load_tools()
        self.tool_instances = {}

        if config.CORE_DEBUG_MODE:
            print("\n[CORE] 🔥 Initialization Complete")
            print("=================================")
            print("[CORE] 🛠️ Loaded Tools:")

            for tool_name, tool_info in self.tools.items():
                actions = tool_info.get("actions", {})
                params = tool_info.get("params", {})

                # ✅ Display tool name and available actions
                print(f"  ✅ {tool_name} (Actions: {', '.join(actions.keys()) or '⚠ No Actions Found'})")

                # ✅ Display parameters per action
                for action, param_list in params.items():
                    print(f"    🔹 {action}: {param_list}")

            print("=================================\n")

    def load_tools(self):
        """Dynamically loads and flattens tools for easy lookup."""
        raw_tools = toolslist.get_tools_list()
        tools = {}

        for category, tool_dict in raw_tools.items():
            for tool_name, tool_info in tool_dict.items():
                if tool_info.get("module_class"):
                    tools[tool_name] = tool_info
                else:
                    print(f"[Warning] Tool '{tool_name}' missing class reference.")

        return tools

    def get_tool_instance(self, tool_name):
        """Retrieve or create a tool instance for execution."""
        if tool_name not in self.tools:
            return None, f"[Error] Tool '{tool_name}' not found."

        if tool_name not in self.tool_instances:
            try:
                self.tool_instances[tool_name] = self.tools[tool_name]['module_class']()
            except Exception as e:
                return None, f"[Error] Failed to initialize {tool_name}: {str(e)}"

        return self.tool_instances[tool_name], None

    def call_tool(self, tool_name, tool_action, tool_params):
        """Calls a tool dynamically and ensures all required parameters are provided."""
        tool_instance, error = self.get_tool_instance(tool_name)
        if error:
            return error

        if not hasattr(tool_instance, tool_action):
            return f"[Error] Tool '{tool_name}' does not support action '{tool_action}'."

        # ✅ Ensure correct parameter unpacking
        try:
            method = getattr(tool_instance, tool_action)

            if config.CORE_DEBUG_MODE:
                print(f"\n[CORE] 🚀 Running {tool_name}.{tool_action} with:")
                print(f"      🔹 Parameters: {tool_params}")

            return method(**tool_params)  # ✅ Ensure params are passed correctly

        except TypeError as e:
            return f"[Error] Failed to execute {tool_name} ({tool_action}): {str(e)}"

    def safe_execute_tools(self, tools, task_summary):
        """Executes multiple tools in parallel using the correct task summary and formatted time."""
        results = {}

        for tool_data in tools:
            tool_name = tool_data["name"]
            tool_action = tool_data["action"]
            tool_params = tool_data.get("params", {})

            if config.CORE_DEBUG_MODE:
                print(f"\n[CORE] 🔄 Preparing to run: {tool_name}.{tool_action}")
                print(f"[CORE] 🛠️ Parameters Passed: {tool_params}")

            result = self.call_tool(tool_name, tool_action, tool_params)

            # ✅ Fix: Ensure results are stored uniquely per tool & action
            results[f"{tool_name}_{tool_action}"] = result  

        return results

    def classify_input(self, user_input, recent_tasks, conversation_history, formatted_tools):
        """Classifies user input dynamically, determining if tools are needed and listing possible candidates."""

        classification_prompt = PromptManager.classification_prompt(user_input, recent_tasks, conversation_history, formatted_tools)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": classification_prompt}],
            api_key=config.OPENAI_API_KEY
        )
        classification = json.loads(response['choices'][0]['message']['content'].strip())

        # ✅ Failsafe: Ensure structure is valid
        needs_tool = classification.get("needs_tool", False)
        possible_tools = classification.get("possible_tools", []) if needs_tool else []

        if needs_tool and not isinstance(possible_tools, list):
            print("[CORE] ⚠ Invalid tool list format, defaulting to empty list.")
            possible_tools = []

        return {"needs_tool": needs_tool, "possible_tools": possible_tools}

    def detect_task(self, user_input, recent_tasks, conversation_history, formatted_tools):
        """Detects intent, task details, required tools, and missing information dynamically."""
        try:
            # 🔍 **Generate Prompt for Task Detection**
            task_prompt = PromptManager.task_detection_prompt(user_input, recent_tasks, conversation_history, formatted_tools)

            # 🚀 **Call OpenAI API (Single API Call)**
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": task_prompt}],
                api_key=config.OPENAI_API_KEY
            )

            # 🔍 **Extract & Parse JSON Response Safely**
            raw_response = response['choices'][0]['message']['content'].strip()

            structured_task = json.loads(raw_response)  # Parse JSON directly

            # 🚨 **Prevent Execution if Uncertain**
            if structured_task.get("intent") == "uncertain":
                structured_task["tools"] = []  # Block accidental tool execution

            # 🚨 **Debug Mode: Print Response for Analysis**
            if config.CORE_DEBUG_MODE:
                print("\n[CORE] ✅ Task Detection Results:")
                print(json.dumps(structured_task, indent=4, ensure_ascii=False))

            return structured_task

        except json.JSONDecodeError as e:
            if config.CORE_DEBUG_MODE:
                print("\n[CORE] ❌ JSON Decoding Failed in detect_task()")
                print(f"[CORE] 🔍 Raw Response (Before Parsing): {raw_response}")  # Log raw response
                print(f"[CORE] ⚠️ JSON Error Details: {str(e)}")  # Show exact JSON error

            return {}

        except Exception as e:
            print(f"\n[CORE] ❌ Unexpected Error in detect_task(): {str(e)}")
            return {}

    def process_input(self, user_input):
        """Fully new system: One API call handles classification + task detection + execution with enhanced safety & mixed input support."""

        if not isinstance(user_input, str) or not user_input.strip():
            return "[Error] No valid input received."

        if config.CORE_DEBUG_MODE:
            print(f"\n[CORE] 📝 Processing Input: {user_input}")

        self.memory.add_message("user", user_input)
        recent_tasks = self.memory.get_recent_tasks()
        conversation_history = self.memory.get_context()

        formatted_tools = "\n".join(
            f'- "{tool}" (Actions: {", ".join(f"{action}: {params}" for action, params in info["params"].items())})'
            for tool, info in self.tools.items()
        )

        structured_task = self.detect_task(user_input, recent_tasks, conversation_history, formatted_tools)

        # 🔍 **Retrieve Intent & Confidence Score**
        intent = structured_task.get("intent", "chat")
        confidence = structured_task.get("confidence", 50)  # Default confidence 50%

        if config.CORE_DEBUG_MODE:
            print(f"\n[CORE] 🧠 Classification Result: {intent} (Confidence: {confidence}%)")
            print(f"[CORE] Recent Tasks: {recent_tasks}\n")

        if intent == "chat":
            return self.chat_module.generate_response(
                {"context": conversation_history, "user_input": user_input}
            )

        # 🚨 **Block Execution if Intent Is Uncertain**
        if intent == "uncertain":
            return self.chat_module.generate_response(
                {"context": conversation_history,
                "user_input": user_input,
                "clarification": "I'm not sure what you're asking. Could you rephrase or provide more context?"},
                mode="clarification"
            )

        # 🚨 **Block Execution if Critical Params Are Missing**
        if structured_task.get("critical_missing_params"):
            missing_params = ", ".join(structured_task["critical_missing_params"])
            if config.CORE_DEBUG_MODE:
                print(f"[CORE] 🚨 Missing Params Detected: {missing_params}")
            return self.chat_module.generate_response(
                {"context": conversation_history,
                "user_input": user_input,
                "clarification": f"Before I create the event, I need: **{missing_params}**. Could you provide these details?"},
                mode="clarification"
            )

        # 🚀 **Handle Mixed Input (Chat + Task Execution)**
        if intent == "mixed":
            chat_response = self.chat_module.generate_response(
                {"context": conversation_history, "user_input": user_input}
            )
            tool_results = self.safe_execute_tools(
                structured_task["tools"], structured_task["summary"]
            )

            formatted_results = "\n".join(
                f"- **{tool['name']} ({tool['action']})** → {tool_results.get(tool_key, '[Error] No execution result')}"
                if (tool_key := f"{tool['name']}_{tool['action']}") in tool_results
                else f"- **{tool['name']} ({tool['action']})** → [Error] No execution result found."
                for tool in structured_task["tools"]
            ) if isinstance(tool_results, dict) else "[Error] Tool execution results are not in dictionary format."

            if config.CORE_DEBUG_MODE:
                print(f"\n[CORE] 🏁 Tool Execution Results: {formatted_results}")

            return f"{chat_response}\n\n{formatted_results}" if formatted_results else chat_response

        # 🚀 **Handle Task Execution (Only if Ready)**
        elif intent == "task":
            tool_results = self.safe_execute_tools(
                structured_task["tools"], structured_task["summary"]
            )

            structured_task["tool_outputs"] = tool_results
            structured_task["tools_used"] = structured_task["tools"]
            self.memory.add_recent_tasks(structured_task)

            formatted_results = "\n".join(
                f"- **{tool['name']} ({tool['action']})** → {tool_results.get(tool_key, '[Error] No execution result')}"
                if (tool_key := f"{tool['name']}_{tool['action']}") in tool_results
                else f"- **{tool['name']} ({tool['action']})** → [Error] No execution result found."
                for tool in structured_task["tools_used"]
            ) if isinstance(tool_results, dict) else "[Error] Tool execution results are not in dictionary format."

            if config.CORE_DEBUG_MODE:
                print(f"\n[CORE] 🏁 Tool Execution Results: {formatted_results}")

            return self.chat_module.generate_response(
                {"context": conversation_history, "formatted_results": formatted_results}, mode="tool"
            )
