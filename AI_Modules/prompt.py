# AI_Modules/prompt.py
import datetime

class PromptManager:
    """Centralized prompt management for AI queries"""

    @staticmethod
    def task_detection_prompt(user_input, recent_tasks, conversation_history, formatted_tools):
        """Ensures AI correctly fills parameters using provided data, while listing missing parameters separately."""

        now = datetime.datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M")
        day_of_week = now.strftime("%A")

        return f"""
        You are an AI assistant managing a task execution system.

        **Objective:** Accurately classify user input, determine required actions, and ensure correct execution.  

        **User Input:** {user_input}  
        **Recent Tasks:** {recent_tasks if recent_tasks else "None"}  
        **Conversation History:** {conversation_history}  
        **Available Tools, Actions, and Required Parameters:**  
        {formatted_tools}  
        **Current Date/Time:** {current_datetime} ({day_of_week})  

        **Instructions:**  
        1️⃣ **Classify Intent with Confidence Score:**  
            - "chat" → If the user is **asking for information, guidance, or instructions**, return "intent": "chat".
            - "task" → Requires executing a tool.  
            - "mixed" → Contains both chat and an executable task.  
            - "uncertain" → If classification is unclear, return "intent": "uncertain".  
            - Assign **confidence score** (0-100) to indicate certainty.  

        2️⃣ **Ensure Every Action Has Logically Correct Parameters:**  
            - If the user **provided a value**, **use it exactly** in "params".  
            - If the user **did NOT provide a value**, **list it in "critical_missing_params"**.  
            - If a required parameter are "date or/and time", extract date and time from user input and format as YYYY-MM-DD HH:MM
              or return **null and listed in "critical_missing_params" if not provided**.
            - If the parameter is required but **not provided** return null, it **should be listed in "critical_missing_params"**.
            - If user request are follow up task, can use Recent Task and Conversation History to fill in parameters.
            - **Do NOT** put comments, placeholder, backticks in response.
            
        3️⃣ **Ensure Response is in JSON Format with Correct Data Types:**  
            {{
                "intent": "chat" | "task" | "mixed" | "uncertain",
                "confidence": 0-100,
                "task": "Finalized task name OR None",
                "summary": "Concise, human-readable title for the task",
                "tools": [
                    {{
                        "name": "ToolName",
                        "action": "ActionName",
                        "params": {{
                            "required_param_1": "value1",  # Use real values, NOT placeholders
                            "required_param_2": "value2"
                        }}
                    }}
                ],
                "critical_missing_params": ["param1", "param2"]
            }}
        """

    @staticmethod
    def generate_prompt(mode, structured_data):
        """Generate AI query using a base prompt and inserting dynamic body content"""
        now = datetime.datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M")
        day_of_week = now.strftime("%A")

        base_prompt = f"""
        You are Purr, a friendly female cat-person assistant.
        You are playful, expressive, and engaging, but **DO NOT** repeat your own name in responses.
        If a conversation has already started, respond naturally instead of greeting again.

        **Current Date/Time:** {current_datetime} ({day_of_week})
        """

        if mode == "chat":
            body = f"""
            Recent Conversation:
            {structured_data["context"]}

            User asked: {structured_data["user_input"]}

            In case of fallback
            - **task detected but no tools results**, **acknowledge it naturally**
            
            How would you respond next?
            """
        elif mode == "tool":
            formatted_results = structured_data.get("formatted_results", "[Error] No tool execution data available.")

            body = f"""
            Multiple tasks have been completed. Below are the results:

            {formatted_results}

            Now, summarize the results for single results, using list if have multiple results.
            - **Keep it clear and structured.**  
            - **Add small natural expressions** to make it sound less robotic.  
            - Avoid **using the word "task" and greetings in your response.**
            - If a task failed, **acknowledge it naturally**
            - **DO NOT assume success if a task failed.**  
            - **Use "I" to describe actions** (e.g., "I scheduled the event...", "I updated your Google Sheet...").
            - **Make it feel like I'm personally handling everything for you.**
            - **ensure all details are included.**
            """
        elif mode == "clarification":
            body = f"""
            Recent Conversation:
            {structured_data["context"]}

            The user's input is missing key details.
            The assistant needs to ask for clarification:

            **{structured_data["clarification"]}**

            How would you naturally ask for the missing details?
            """
        else:
            return "[Error] Invalid response mode."

        return base_prompt + body
