from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import config
import memory
import asyncio

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[bot.py] Received /start command from chat_id: {update.message.chat_id}")
    memory.save_chat_id(update.message.chat_id)
    await update.message.reply_text("Hola! Soy tu asistente personal. En qué puedo ayudarte?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_message = update.message.text
    print(f"[bot.py] Received message from chat_id {chat_id}: {user_message}")
    memory.save_chat_id(chat_id)
    
    print(f"[bot.py] Sending message to API: http://localhost:5000/process_message")
    response = requests.post("http://localhost:5000/process_message", json={"message": user_message, "chat_id": chat_id})
    print(f"[bot.py] Received response from API: {response.json()}")
    
    await update.message.reply_text(response.json().get("response"))

if __name__ == "__main__":
    print("[bot.py] Starting bot...")
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
