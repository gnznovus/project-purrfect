# config.example.py
# ============================================================================
# Copy this file to config.py and fill in your actual API keys and settings
# NEVER commit the actual config.py with real API keys to GitHub!
# ============================================================================

import os

# ============== API KEYS ==============
# Get from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Get from: https://console.cloud.google.com/
GOOGLE_SHEET_API_KEY = "your-google-sheet-api-key-here"

# ============== PLATFORM ==============
# Options: "terminal" or "telegram"
INPUT_PLATFORM = "terminal"

# ============== TELEGRAM ==============
# Get token from: https://t.me/BotFather
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token-here"
BOT_USERNAME = "PurrAssistantBot"
TELEGRAM_DM = True  # True for DM mode, False for group mode

# ============== GOOGLE ==============
# Path to your Google credentials JSON file
# Download from: https://console.cloud.google.com/
GOOGLE_SHEET_CREDENTIALS_PATH = 'purrfect_sheet.json'

# ============== DEBUG ==============
# Enable/disable debug output for different modules
CHAT_DEBUG_MODE = True
CORE_DEBUG_MODE = False
SWITCH_DEBUG_MODE = False
TOOLS_DEBUG_MODE = False
ML_DEBUG_MODE = True
LOCAL_VOICE = False

# ============== ML TRAINING SETTINGS ==============
# Machine Learning model training configuration
ML_CLARIFICATION_MODE = True
ML_MAX_TRAIN_SIZE = 1000
ML_AUTO_TRAIN_THRESHOLD = 100
ML_AUTO_TRAIN = True
ML_AUTO_RETRAIN = True
ML_BATCH_TRAIN_SIZE = 10
ML_CONFIDENCE_TUNING = True
ML_CONFIDENCE_THRESHOLD = 0.70

# ============== ML NUKE BUTTON ==============
# ⚠️ DANGEROUS - Only use if you know what you're doing!
ML_SELF_DESTRUCTION = False

# ============== MAIN PATH SETTINGS ==============
# These auto-create directories for storing data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_PATH = os.path.join(BASE_DIR, "Storage")
TOOLS_STORAGE_PATH = os.path.join(STORAGE_PATH, "Tools")
MODEL_PATH = os.path.join(STORAGE_PATH, "Models")

# ============== TOOLS PATH SETTINGS ==============
VOICE_STORAGE_PATH = os.path.join(TOOLS_STORAGE_PATH, "Voice")
IMAGE_STORAGE_PATH = os.path.join(TOOLS_STORAGE_PATH, "Image")
CALENDAR_STORAGE_PATH = os.path.join(TOOLS_STORAGE_PATH, "Calendar")
SHEET_STORAGE_PATH = os.path.join(TOOLS_STORAGE_PATH, "Sheet")

# ============== ML PATH SETTINGS ==============
TRAINING_DATA_PATH = os.path.join(MODEL_PATH, "Training_Data.txt")
RETRAIN_DATA_PATH = os.path.join(MODEL_PATH, "Retrain_Data.txt")

# ============== AUTO CREATE DIRECTORIES ==============
os.makedirs(STORAGE_PATH, exist_ok=True)
os.makedirs(TOOLS_STORAGE_PATH, exist_ok=True)
os.makedirs(MODEL_PATH, exist_ok=True)
os.makedirs(VOICE_STORAGE_PATH, exist_ok=True)
