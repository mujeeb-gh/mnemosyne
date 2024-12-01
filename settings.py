from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
# General settings
APP_NAME = "Mnemosyne"
VERSION = "1.0.0"
DEBUG = True
DEFAULT_CAM = 0
IP_WEBCAM_IP = "http://192.168.69.44:8080"

# Paths
BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / 'src'
ASSETS_DIR = SRC_DIR / 'assets'
VECTOR_DB_DIR = BASE_DIR / 'vector_db'

# Database settings
# DB_HOST = "localhost"
# DB_PORT = 5432
# DB_NAME = "mnemosyne_db"
# DB_USER = "user"
# DB_PASSWORD = "password"

# Logging settings
# LOG_FILE = "mnemosyne/logs/app.log"
# LOG_LEVEL = "DEBUG"

