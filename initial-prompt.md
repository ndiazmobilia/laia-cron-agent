### **Prompt for Building a Dual-AI, API-Driven Telegram Assistant**

**Role & Goal:**

You are a senior AI architect. Your mission is to engineer an advanced, highly modular personal assistant delivered via a Telegram bot. The system's intelligence will be powered by **two distinct OpenAI Assistant instances**, each with a specialized role, communicating through a central REST API to ensure maximum flexibility and code reuse.

**Core Architecture: Centralized API & Dual AI Strategy**

The foundation of this project is a REST API (using Flask/FastAPI) that serves as the single point of entry for all message processing. This design decouples the input sources (live bot, scheduled tasks) from the processing logic.

The system will employ two specialized AI Assistants:

1.  **The Listener AI:** This is the primary conversational interface. Its persona is helpful, proactive, and skilled at understanding complex user requests. Its main goal is to chat with the user and use tools (like the scheduler) on their behalf.
2.  **The Notifier AI:** This AI's role is to deliver scheduled messages. Its persona is more direct and context-aware. It understands it is delivering a pre-scheduled notification and frames its message accordingly (e.g., "Hi there! Just dropping in with your 10 AM reminder: Time to walk the dog.").

**Assistant Lifecycle Management:**

The application must manage the OpenAI Assistant instances intelligently:

*   **On Startup:** The system will check for `LISTENER_ASSISTANT_ID` and `NOTIFIER_ASSISTANT_ID` in the environment variables.
*   **If IDs Exist:** It will use these IDs to interact with the pre-existing OpenAI Assistants.
*   **If IDs are Missing:** It will, on its first run, programmatically create the two required Assistants using the OpenAI API. Each Assistant will be configured with its own specific system prompt and toolset.
*   **Output New IDs:** After creating new Assistants, the application **must print the new IDs to the console**. This provides the user with the necessary values to add to their `.env` file for persistent operation on subsequent runs.

**Component Breakdown & Responsibilities:**

*   `main.py`: The application's entry point. It handles the initial Assistant ID check and creation, then launches the API server and the Telegram bot listener in separate threads.
*   `api.py`: Hosts the web server. It exposes a primary endpoint (e.g., `/process_message`) that accepts a JSON payload containing `message`, `chat_id`, and an optional `source` field (e.g., `"source": "notifier"`).
*   `message_handler.py`: The central router, called by the API. It inspects the incoming payload:
    *   If the message starts with `/`, it executes a direct command function.
    *   If the `source` is `"notifier"`, it forwards the request to the Notifier AI.
    *   Otherwise, it forwards the request to the Listener AI.
*   `listener_handler.py`: Manages all interactions with the Listener AI Assistant. It contains the specific system prompt for conversational interactions.
*   `notifier_handler.py`: Manages all interactions with the Notifier AI Assistant. It contains the specific system prompt for delivering notifications.
*   `scheduler.py`: An AI tool callable by the Listener AI. When creating a `cron` job, it must construct a `curl` command that calls the `/process_message` endpoint and includes `"source": "notifier"` in the JSON payload.
*   `config.py`: Loads and provides access to all environment variables.
*   `memory.py`: A simple utility to persist and retrieve user `chat_id`.
*   `requirements.txt`: Lists all dependencies (`python-telegram-bot`, `openai`, `python-dotenv`, `Flask`).

**Execution Flow Example (AI Reminder & Notification):**

1.  A user sends: "Hey, remind me to check my email in 15 minutes."
2.  `bot.py` receives the message and POSTs to `http://localhost:5000/process_message` with the message and `chat_id`.
3.  `api.py` calls `message_handler.py`. Seeing no slash and no `source`, it routes to `listener_handler.py`.
4.  The Listener AI understands the request and uses the `scheduler.py` tool.
5.  `scheduler.py` creates a `cron` job for 15 minutes in the future. The command is a `curl` call to the API, crucially with the payload: `{"message": "Check your email", "chat_id": "...", "source": "notifier"}`.
6.  The Listener AI confirms with the user: "You got it. I'll remind you to check your email in 15 minutes."
7.  *15 minutes later...* `cron` executes the `curl` command.
8.  `api.py` receives the request. `message_handler.py` sees `"source": "notifier"` and routes the request to `notifier_handler.py`.
9.  The Notifier AI processes the message ("Check your email") and, using its specialized prompt, generates a friendly, context-appropriate notification like "Hey! This is your friendly reminder to check your email." This is sent to the user.

**Constraints:**

*   Do not create the `.env` file. Assume it is already present and contains `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY`. The user will be responsible for adding the `LISTENER_ASSISTANT_ID` and `NOTIFIER_ASSISTANT_ID` after the first run.
