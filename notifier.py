import sys
import requests
import json
import os
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes
import config

async def send_telegram_message(chat_id: str, text: str):
    """Sends a message to the specified chat ID using the Telegram bot."""
    print(f"[notifier.py] Sending Telegram message to chat_id {chat_id}: {text}")
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    context = ContextTypes.DEFAULT_TYPE(application)
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
        print(f"[notifier.py] Message sent successfully to chat_id {chat_id}.")
    except Exception as e:
        print(f"[notifier.py] Error sending message to chat_id {chat_id}: {e}")

async def main():
    if len(sys.argv) < 3:
        print("[notifier.py] Usage: python3 notifier.py \"<message>\" <chat_id>")
        sys.exit(1)

    message = sys.argv[1]
    chat_id = sys.argv[2]

    print(f"[notifier.py] Notifier received message: '{message}' for chat_id: {chat_id}")

    api_url = "http://localhost:5000/process_message"
    payload = {"message": message, "chat_id": chat_id, "source": "notifier"}
    headers = {"Content-Type": "application/json"}

    try:
        print(f"[notifier.py] Calling API: {api_url} with payload: {payload}")
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        api_response = response.json()
        print(f"[notifier.py] API response: {api_response}")

        response_text = api_response.get("response", "No response text from API.")
        await send_telegram_message(chat_id, response_text)

    except requests.exceptions.RequestException as e:
        error_message = f"[notifier.py] Error calling API: {e}"
        print(error_message)
        await send_telegram_message(chat_id, f"Error processing your request: {e}")
    except json.JSONDecodeError as e:
        error_message = f"[notifier.py] Error decoding JSON response: {e}"
        print(error_message)
        await send_telegram_message(chat_id, f"Error processing API response: {e}")
    except Exception as e:
        error_message = f"[notifier.py] An unexpected error occurred: {e}"
        print(error_message)
        await send_telegram_message(chat_id, f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
