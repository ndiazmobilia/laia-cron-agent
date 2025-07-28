import json

MEMORY_FILE = "chat_memory.json"

def save_chat_id(chat_id):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"chat_id": chat_id}, f)

def load_chat_id():
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            return data.get("chat_id")
    except FileNotFoundError:
        return None
