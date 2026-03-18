import config
from AI_Modules.chat import ChatModule
from Memory_Modules.memory import MemoryBuffer
from Utils_Modules import toolslist

class Core:
    def __init__(self, switch):
        """Initialize CORE with Switch, Memory, and Tool Modules."""
        self.switch = switch
        self.chat_module = ChatModule()
        self.memory = MemoryBuffer(buffer_size=10)
        self.tools = self.load_tools()  # Still loads tools, just unused for now

        if config.CORE_DEBUG_MODE:
            print("\n[CORE] 🔥 Initialization Complete")
            print("=================================")
            print("[CORE] 🛠️ Loaded Tools:")

            for tool_name, tool_info in self.tools.items():
                actions = tool_info.get("actions", {})
                params = tool_info.get("params", {})
                print(f"  ✅ {tool_name} (Actions: {', '.join(actions.keys()) or '⚠ No Actions Found'})")
                for action, param_list in params.items():
                    print(f"    🔹 {action}: {param_list}")
            print("=================================\n")

    def load_tools(self):
        """Dynamically loads and flattens tools for future use."""
        raw_tools = toolslist.get_tools_list()
        tools = {}

        for category, tool_dict in raw_tools.items():
            for tool_name, tool_info in tool_dict.items():
                if tool_info.get("module_class"):
                    tools[tool_name] = tool_info
                else:
                    print(f"[Warning] Tool '{tool_name}' missing class reference.")

        return tools

    def process_input(self, user_input):
        """Chat-only mode: receives input, generates response using context."""
        if not isinstance(user_input, str) or not user_input.strip():
            return "[Error] No valid input received."

        if config.CORE_DEBUG_MODE:
            print(f"\n[CORE] 📝 Processing Input (Chat-Only Mode): {user_input}")

        self.memory.add_message("user", user_input)
        conversation_history = self.memory.get_context()

        response = self.chat_module.generate_response(
            {"context": conversation_history, "user_input": user_input}
        )
        
        self.memory.add_message("assistant", response)

        return response