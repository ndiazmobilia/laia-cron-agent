from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import config
import memory
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Received /start command from chat_id: {update.message.chat_id}")
    memory.save_chat_id(update.message.chat_id)
    await update.message.reply_text("Hola! Soy tu asistente personal. En qué puedo ayudarte?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_message = update.message.text
    logging.info(f"Received message from chat_id {chat_id}: {user_message}")
    memory.save_chat_id(chat_id)
    
    logging.info(f"Sending message to API: http://localhost:5000/process_message")
    response = requests.post("http://localhost:5000/process_message", json={"message": user_message, "chat_id": chat_id})
    logging.info(f"Received response from API: {response.json()}")
    
    await update.message.reply_text(response.json().get("response"))

if __name__ == "__main__":
    logging.info("Starting bot...")
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
