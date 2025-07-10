import logging
import os
import threading
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google_calendar_utils import get_calendar_service_service_account, start_watching_calendar, stop_watching_calendar
from webhook_server import app
from watch_config import save_watch_config, load_watch_config, clear_watch_config

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=None,
    )
    await update.message.reply_text("I am a bot that can notify you of new emails.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def start_watching_calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts watching the primary Google Calendar for events."""
    try:
        service = get_calendar_service_service_account()
        webhook_url = os.getenv("WEBHOOK_URL") + "/webhook"
        if not webhook_url:
            await update.message.reply_text("WEBHOOK_URL environment variable not set.")
            return

        response = start_watching_calendar(service, 'primary', webhook_url)
        save_watch_config(response['id'], response['resourceId'])
        logger.info(f"Started watching calendar: {response}")
        await update.message.reply_text("Started watching primary calendar for events.")
    except Exception as e:
        logger.error(f"Error starting calendar watch: {e}")
        await update.message.reply_text(f"An error occurred: {e}")

async def stop_watching_calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops watching the primary Google Calendar."""
    config = load_watch_config()
    if not config:
        await update.message.reply_text("No active calendar watch found to stop.")
        return

    try:
        service = get_calendar_service_service_account()
        response = stop_watching_calendar(service, config['channel_id'], config['resource_id'])
        clear_watch_config()
        logger.info(f"Stopped watching calendar: {response}")
        await update.message.reply_text("Stopped watching primary calendar.")
    except Exception as e:
        logger.error(f"Error stopping calendar watch: {e}")
        await update.message.reply_text(f"An error occurred: {e}")

def run_flask_app():
    """Runs the Flask web server in a separate thread."""
    # In production, use a Gunicorn server instead of the Flask development server
    # For example: gunicorn --bind 0.0.0.0:8080 webhook_server:app
    app.run(port=8080)

def main() -> None:
    """Start the bot."""
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    application = Application.builder().token(telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("start_watching_calendar", start_watching_calendar_command))
    application.add_handler(CommandHandler("stop_watching_calendar", stop_watching_calendar_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.bot.delete_webhook()

    logger.info("Bot is running. Press Ctrl-C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()