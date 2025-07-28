# Laia Cron Agent

This project is a Telegram bot that uses OpenAI assistants to provide personalized responses. It can handle incoming messages and send scheduled notifications.

## Features

- **Telegram Bot Integration:** Interacts with users through a Telegram bot.
- **OpenAI Assistants:** Uses OpenAI assistants to generate intelligent and context-aware responses.
- **Dual Assistant Architecture:** Employs two distinct assistants:
    - **Listener AI:** Handles direct user messages.
    - **Notifier AI:** Manages scheduled notifications.
- **Scheduled Notifications:** A scheduler sends periodic messages to the user.
- **Persistent Chat ID:** Remembers the user's chat ID for sending notifications.
- **Flask API:** A simple API to process messages, decoupling the bot from the core logic.

## How It Works

1.  **Telegram Bot (`bot.py`):** The bot receives messages from the user and forwards them to the Flask API.
2.  **Flask API (`api.py`):** The API receives the message and passes it to the `message_handler`.
3.  **Message Handler (`message_handler.py`):** This is the core of the application. It determines whether the message is from a direct user interaction or a scheduled notification and routes it to the appropriate handler (`listener_handler` or `notifier_handler`). It also creates the OpenAI assistants if they don't exist, using prompts from `listener_prompt.md` and `notifier_prompt.md`.
4.  **Assistant Handlers (`listener_handler.py`, `notifier_handler.py`):** These handlers interact with the OpenAI API, creating threads, sending messages, and retrieving the assistant's response.
5.  **Scheduler (`scheduler.py`):** This script runs in the background and sends a notification to the user at a regular interval. It communicates with the API to send the notification.
6.  **Memory (`memory.py`):** The `chat_id` of the user is saved to a JSON file (`chat_memory.json`) so the scheduler can send notifications.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/laia-cron-agent.git
    cd laia-cron-agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file and add your API keys:**
    ```
    TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    OPENAI_API_KEY="your_openai_api_key"
    ```

## Usage

1.  **Run the Flask API:**
    ```bash
    python api.py
    ```

2.  **Run the Telegram bot:**
    ```bash
    python bot.py
    ```

3.  **Run the scheduler:**
    ```bash
    python scheduler.py
    ```

4.  **Interact with the bot on Telegram.**

## Project Structure

```
.
├── api.py              # Flask API to process messages
├── bot.py              # Main Telegram bot
├── config.py           # Configuration loader
├── initial-prompt.md   # Initial prompt for the assistant
├── listener_handler.py # Handles interaction with the Listener AI
├── listener_prompt.md  # Prompt for the Listener AI
├── memory.py           # Saves and loads the chat ID
├── message_handler.py  # Routes messages to the correct handler
├── notifier_handler.py # Handles interaction with the Notifier AI
├── notifier_prompt.md  # Prompt for the Notifier AI
├── README.md           # This file
├── requirements.txt    # Python dependencies
└── scheduler.py        # Sends scheduled notifications
```