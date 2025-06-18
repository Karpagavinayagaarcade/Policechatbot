import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Document processing settings
ALLOWED_DOCUMENT_TYPES = ['docx', 'xlsx', 'xls']
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Google Sheets settings
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Chatbot settings
DEFAULT_MODE = 'general'
SUPPORTED_MODES = ['general', 'kids', 'emergency', 'legal']

# Emergency contact information
EMERGENCY_CONTACTS = {
    'police': '911',
    'ambulance': '911',
    'fire': '911',
    'poison_control': '1-800-222-1222',
    'child_help': '1-800-422-4453'
}

# Kids mode settings
KIDS_MODE_AGE_RANGE = (5, 12)
KIDS_MODE_KEYWORDS = {
    'safety': ['safe', 'danger', 'stranger', 'help'],
    'emergency': ['emergency', '911', 'help', 'danger'],
    'police': ['police', 'officer', 'cop', 'law']
}

# NLP settings
NLP_SETTINGS = {
    'min_confidence': 0.6,
    'max_response_length': 500,
    'language': 'en'
}

# Offline mode settings
OFFLINE_MODE = {
    'enabled': True,
    'data_sync_interval': 24 * 60 * 60  # 24 hours in seconds
}

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FILE = 'police_chatbot.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 