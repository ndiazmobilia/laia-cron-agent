import json
import os

CONFIG_FILE = "watch_config.json"

def save_watch_config(channel_id, resource_id):
    """Saves the watch channel configuration to a JSON file."""
    config = {
        "channel_id": channel_id,
        "resource_id": resource_id
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_watch_config():
    """Loads the watch channel configuration from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def clear_watch_config():
    """Clears the watch channel configuration file."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
