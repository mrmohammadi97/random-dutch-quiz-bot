import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # SQLite database path - stores in project root
    DATABASE_PATH = PROJECT_ROOT / "quiz_bot.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Quiz settings
    NUMBER_RANGE_MIN = int(os.getenv('NUMBER_RANGE_MIN', 1))
    NUMBER_RANGE_MAX = int(os.getenv('NUMBER_RANGE_MAX', 1000))
    TIME_MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]


settings = Settings()