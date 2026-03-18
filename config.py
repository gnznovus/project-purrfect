# config.py
import os

# ============== API KEYS ==============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_API_KEY = os.getenv("GOOGLE_SHEET_API_KEY")

# ============== PLATFORM ==============
INPUT_PLATFORM = "terminal"

# ============== TELEGRAM ==============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = "PurrAssistantBot"
TELEGRAM_DM = True

# ============== GOOGLE ==============
GOOGLE_SHEET_CREDENTIALS_PATH = 'purrfect_sheet.json'

# ============== DEBUG ==============
CHAT_DEBUG_MODE = True
CORE_DEBUG_MODE = False
SWITCH_DEBUG_MODE = False
TOOLS_DEBUG_MODE = False
ML_DEBUG_MODE = True
LOCAL_VOICE = False

# ============== # ML TRAINING SETTINGS ==============
ML_CLARIFICATION_MODE = True
ML_MAX_TRAIN_SIZE = 1000
ML_AUTO_TRAIN_THRESHOLD = 100
ML_AUTO_TRAIN = True
ML_AUTO_RETRAIN = True
ML_BATCH_TRAIN_SIZE = 10
ML_CONFIDENCE_TUNING = True
ML_CONFIDENCE_THRESHOLD = 0.70

# ============== # ML NUKE BUTTON ==============
ML_SELF_DESTRUCTION = False # DANGEROUS don't use if you don't know what you're doing

# ============== MAIN PATH SETTINGS ==============
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
os.makedirs(IMAGE_STORAGE_PATH, exist_ok=True)
os.makedirs(CALENDAR_STORAGE_PATH, exist_ok=True)
os.makedirs(SHEET_STORAGE_PATH, exist_ok=True)
