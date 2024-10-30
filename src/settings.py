# settings.py

# General settings
APP_NAME = "Mnemosyne"
VERSION = "1.0.0"
DEBUG = True
DEFAULT_CAM = 0
IP_WEBCAM_IP = "http://192.168.69.44:8080"

# Paths
DATA_PATH = "mnemosyne/data/"
MODEL_PATH = "mnemosyne/models/"

# Database settings
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mnemosyne_db"
DB_USER = "user"
DB_PASSWORD = "password"

# Logging settings
LOG_FILE = "mnemosyne/logs/app.log"
LOG_LEVEL = "DEBUG"

# Other settings
RANDOM_SEED = 42
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001