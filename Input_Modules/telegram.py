from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import config
import os

class TelegramBot:
    """Handles Telegram bot interactions in a group chat or DM."""

    def __init__(self, switch):
        self.switch = switch
        self.is_listening = False
        self.bot_username = config.BOT_USERNAME
        self.dm_mode = config.TELEGRAM_DM
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        self.latest_message = None  # ✅ Store last received message

        # Set up handlers for both text and voice
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

    async def handle_message(self, update: Update, context: CallbackContext):
        """Processes incoming text messages."""
        from CORE_Modules.core import Core  # ✅ Lazy Import to Prevent Circular Import
        core = Core(self.switch)  

        chat_id = update.message.chat_id
        user_text = update.message.text.strip()
        self.latest_message = user_text  # ✅ Store latest message

        print(f"[Telegram] Received (Text): {user_text}")

        # **Handle DM Mode (Always listens)**
        if config.TELEGRAM_DM:
            self.is_listening = True  # ✅ Always active in DM mode

        # **Handle Group Mode Activation**
        elif not self.is_listening:  # ✅ Only activates in Group Mode
            if self.bot_username.lower() in user_text.lower() or "hey purr" in user_text.lower():
                self.is_listening = True
                response = core.chat_module.generate_response("Acknowledge activation")
                print(f"[Telegram] Listening Activated: {response}")
                await context.bot.send_message(chat_id=chat_id, text=response)
                return
        
        # **Check for stop command in Group Mode**
        if self.is_listening and not config.TELEGRAM_DM:
            if "thanks purr" in user_text.lower() or "stop listening" in user_text.lower():
                self.is_listening = False
                response = core.chat_module.generate_response("Acknowledge deactivation")
                print(f"[Telegram] Listening Stopped: {response}")
                await context.bot.send_message(chat_id=chat_id, text=response)
                return

        # **Process Input**
        if self.is_listening:  # ✅ Always listens in DM, only when active in Group
            processed_input = self.switch.get_input()
            print(f"[Telegram] Processed Input: {processed_input}")  

            if processed_input:
                response = core.process_input(processed_input)
                print(f"[Telegram] Core Response: {response}")  
                await context.bot.send_message(chat_id=chat_id, text=response)

    async def handle_voice_message(self, update: Update, context: CallbackContext):
        """Handles incoming voice messages."""
        from CORE_Modules.core import Core
        core = Core(self.switch)

        chat_id = update.message.chat_id
        voice_file = await update.message.voice.get_file()

        print("[Telegram] Received (Voice Message)")

        # **Download voice file**
        file_path = os.path.join(config.VOICE_STORAGE_PATH, f"{voice_file.file_id}.ogg")
        await voice_file.download_to_drive(file_path)

        # **Send to Switch for Voice Processing**
        transcribed_text = self.switch.process_voice(file_path)

        if transcribed_text:
            print(f"[Telegram] Processed Input (Voice): {transcribed_text}")

            # ✅ Send directly to Core (Skip `get_input()`)
            response = core.process_input(transcribed_text)
            print(f"[Telegram] Core Response (Voice): {response}")

            await context.bot.send_message(chat_id=chat_id, text=response)

    def run(self):
        """Starts Telegram bot properly without restarting inside get_input()."""
        print(f"[Telegram Bot] Running as {self.bot_username} in {'DM' if self.dm_mode else 'Group'} mode...")
        self.app.run_polling()  # ✅ Only called once during Switch initialization
