from Input_Modules.telegram import TelegramBot
import config
import os

class Switch:
    def __init__(self):
        self.platform = config.INPUT_PLATFORM
        self.telegram_bot = None
        
        if config.SWITCH_DEBUG_MODE:
            print(f"[Debug] Switch initialized for platform: {self.platform}")

        if self.platform == "telegram":
            self.telegram_bot = TelegramBot(self)  
            self.telegram_bot.run()  

    def detect_input_type(self, user_input):
        """Detects if the input is voice or text."""
        if isinstance(user_input, dict):
            if "voice" in user_input:
                return "voice"
        return "text"

    def process_voice(self, voice_file_path=None):
        """Calls the Voice-to-Text tool for transcription."""
        print(f"[Switch] Voice Input Detected - Calling Voice-to-Text Tool...")

        # Check if the tool is available
        if "voice-to-text tool" in self.tools:
            tool_instance = self.tools["voice-to-text tool"]["module_class"]()
            result = tool_instance.execute(voice_file_path)

            print(f"[Switch] Raw Transcription Output: {result}")  # Log full result

            # Extract the transcribed text properly
            if isinstance(result, dict) and "text" in result:
                transcribed_text = result["text"].strip()
                if transcribed_text:
                    print(f"[Switch] Transcribed Text: {transcribed_text}")
                    return transcribed_text  # Now it returns a string, not a dict!

                print("[Switch] Warning: Voice transcription returned empty text.")
                return "[Error] Transcription failed (empty result)."

            print("[Switch] Warning: Unexpected transcription format.")
            return "[Error] Unexpected transcription format."

        print("[Switch] Voice-to-Text tool not found!")
        return "[Error] Voice-to-Text tool is missing."

    def get_input(self):
        """Returns the latest received input for processing."""
        if self.platform == "terminal":
            user_input = input("You: ").strip()
            if config.SWITCH_DEBUG_MODE:
                print(f"[Debug] Switch received input: {user_input}")  # Debug line for input capture
            return user_input
        
        elif self.platform == "telegram":
            if self.telegram_bot.latest_message:
                message = self.telegram_bot.latest_message

                if isinstance(message, dict) and "voice" in message:
                    print("[Switch] Voice Input Detected - Calling Voice-to-Text Tool...")
                    transcribed_text = self.process_voice(message["voice"])

                    if transcribed_text:  # Ensure it's a valid string
                        print(f"[Switch] Returning Transcription: {transcribed_text}")
                        return transcribed_text

                    print("[Switch] Warning: Voice-to-Text result is empty.")
                    return "[Error] Transcription failed."

                print(f"[Switch] Returning Telegram message: {message}")
                return message
            
            return None  # Avoid returning None if no message received
