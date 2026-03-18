import openai
import config
from typing import Optional
from AI_Modules.prompt import PromptManager

class ChatModule:
    """
    AI-powered chat interface using OpenAI's GPT models.
    
    Handles:
    - Generation of prompts via PromptManager
    - API calls to OpenAI
    - Response formatting and parsing
    
    This module acts as the "brain" of the system, interpreting user intent
    and generating structured outputs for tool execution.
    
    Attributes:
        api_key: OpenAI API key from configuration
    """
    
    def __init__(self) -> None:
        """Initialize Chat Module using API key from config"""
        self.api_key = config.OPENAI_API_KEY

    def generate_response(self, structured_data: dict, mode: str = "chat") -> str:
        """Chat Module generates structured responses based on mode.
        
        Args:
            structured_data: Input data to generate response for
            mode: Response mode (default: "chat")
            
        Returns:
            str: Generated response from AI model
        """
        prompt = PromptManager.generate_prompt(mode, structured_data)

        if config.CHAT_DEBUG_MODE:
            print(f"[Chat Module] Prompt: {prompt}")

        return self.call_openai_model("gpt-3.5-turbo", prompt)

    def call_openai_model(self, model: str, user_input: str) -> str:
        """Chat Module calls OpenAI API for response formatting
        
        Args:
            model: Model identifier (e.g., "gpt-3.5-turbo")
            user_input: Input prompt for the model
            
        Returns:
            str: Model's response
        """
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            api_key=self.api_key
        )
        return response['choices'][0]['message']['content'].strip()
