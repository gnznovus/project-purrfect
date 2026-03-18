import whisper
import requests
import openai
import warnings
import config

NAME = "Voice-to-Text Tool"
DESCRIPTION = "Converts voice messages to text using Whisper AI."

warnings.filterwarnings("ignore")

class VoiceToTextTool:
    """Handles voice-to-text transcription using Whisper AI."""

    def __init__(self):
        """Load Whisper model once to optimize performance."""
        print("[Voice-To-Text] Loading Whisper Model...")
        self.model = whisper.load_model("base")

    def execute(self, audio_file):
        """Processes a voice file and converts it to text."""
        print(f"[Voice-To-Text] Processing file: {audio_file}")  

        try:
            result = self.model.transcribe(audio_file)
            print(f"[Voice-To-Text] Whisper Raw Output: {result}")  

            if isinstance(result, dict) and "text" in result:
                transcribed_text = result["text"].strip()
                if transcribed_text:
                    print(f"[Voice-To-Text] Transcription Successful: {transcribed_text}")
                    return {"text": transcribed_text}  

                print("[Voice-To-Text] Warning: Whisper returned empty text.")
                return {"text": "[Error] No transcription available."}

            print("[Voice-To-Text] Warning: No 'text' field found in Whisper response.")
            return {"text": "[Error] Invalid Whisper output format."}

        except Exception as e:
            print(f"[Voice-To-Text] Error during transcription: {e}")
            return {"text": f"[Error] Failed to process audio: {str(e)}"}

    def download_voice(self, voice_url):
        """Downloads the voice message and saves it locally."""
        file_path = "voice_message.ogg"

        response = requests.get(voice_url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[VoiceToText] Voice message downloaded: {file_path}")
            return file_path
        else:
            print("[VoiceToText] Failed to download voice message.")
            return None

    def transcribe_audio(self, file_path):
        """Uses Whisper to transcribe the downloaded audio file."""
        with open(file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                api_key=config.OPENAI_API_KEY
            )
            return response["text"] if "text" in response else None
