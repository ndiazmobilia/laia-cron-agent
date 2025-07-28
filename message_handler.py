import os
import listener_handler
import notifier_handler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_or_create_assistant(assistant_id_env, assistant_name, prompt_file, tools=[]):
    client = OpenAI()
    print(f"[message_handler.py] Checking for assistant: {assistant_name}")
    if os.getenv(assistant_id_env):
        assistant_id = os.getenv(assistant_id_env)
        print(f"[message_handler.py] Found existing {assistant_name} ID: {assistant_id}")
        return client.beta.assistants.retrieve(assistant_id)

    with open(prompt_file, 'r') as f:
        prompt = f.read()

    print(f"[message_handler.py] Creating new {assistant_name}...")
    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=prompt,
        model="gpt-4o-mini",
        tools=tools
    )

    with open('.env', 'a+') as f:
        f.seek(0)
        if assistant_id_env not in f.read():
            f.write(f'\n{assistant_id_env}={assistant.id}')

    print(f"Created {assistant_name} assistant with ID: {assistant.id}")
    return assistant

def handle_message(message, chat_id, source=None):
    print(f"[message_handler.py] Handling message: '{message}', chat_id='{chat_id}', source='{source}'")
    if message.startswith("/"):
        print("[message_handler.py] Message is a command.")
        # Command handling logic will go here
        return "Command handling not yet implemented."

    if source == "notifier":
        print("[message_handler.py] Message source is notifier.")
        assistant = get_or_create_assistant(
            'NOTIFIER_ASSISTANT_ID',
            'Notifier AI',
            'notifier_prompt.md'
        )
        return notifier_handler.handle_message(message, chat_id, assistant)
    else:
        print("[message_handler.py] Message source is listener.")
        assistant = get_or_create_assistant(
            'LISTENER_ASSISTANT_ID',
            'Listener AI',
            'listener_prompt.md',
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "add_cron_job",
                        "description": "Schedule a task to run at a specific time.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "crontab": {
                                    "type": "string",
                                    "description": "The crontab expression for the schedule."
                                },
                                "message": {
                                    "type": "string",
                                    "description": "The message to be sent as a notification."
                                }
                            },
                            "required": ["crontab", "message"]
                        }
                    }
                }
            ]
        )
        return listener_handler.handle_message(message, chat_id, assistant)