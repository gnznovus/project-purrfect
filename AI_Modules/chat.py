import openai
import config
from AI_Modules.prompt import PromptManager

class ChatModule:
    def __init__(self):
        """Initialize Chat Module using API key from config"""
        self.api_key = config.OPENAI_API_KEY

    def generate_response(self, structured_data, mode="chat"):
        """Chat Module generates structured responses based on mode."""
        prompt = PromptManager.generate_prompt(mode, structured_data)

        if config.CHAT_DEBUG_MODE:
            print(f"[Chat Module] Prompt: {prompt}")

        return self.call_openai_model("gpt-3.5-turbo", prompt)

    def call_openai_model(self, model, user_input):
        """Chat Module calls OpenAI API for response formatting"""
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            api_key=self.api_key
        )
        return response['choices'][0]['message']['content'].strip()
