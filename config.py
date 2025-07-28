import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LISTENER_ASSISTANT_ID = os.getenv("LISTENER_ASSISTANT_ID")
NOTIFIER_ASSISTANT_ID = os.getenv("NOTIFIER_ASSISTANT_ID")
