import os
import json

def add_cron_task(command, time="0 10 * * *"):
    print(f"[cron_manager.py] add_cron_task called with command: '{command}' and time: '{time}'")
    # Escape single quotes in the command to be stored in the crontab

    cron_entry = f"{time} {command}"
    print(f"[cron_manager.py] Creating cron entry: {cron_entry}")
    # Using a temporary file to avoid issues with special characters in the command
    with open("cron_temp", "w") as f:
        f.write(f'{cron_entry}\n')
    print("[cron_manager.py] Wrote cron entry to temporary file.")
    result = os.system("crontab cron_temp")
    print(f"[cron_manager.py] crontab command exit code: {result}")
    os.remove("cron_temp")
    print("[cron_manager.py] Removed temporary file.")
    if result == 0:
        return json.dumps({"status": "success", "details": f"Scheduled command at '{time}'"})
    else:
        return json.dumps({"status": "error", "details": f"Failed to schedule command. The crontab command returned a non-zero exit code: {result}. This is likely due to an invalid crontab expression: '{time}'"})


def remove_cron_task(message_substring):
    print(f"[cron_manager.py] remove_cron_task called with message_substring: '{message_substring}'")
    current_crontab = os.popen('crontab -l').read()
    lines = current_crontab.splitlines()
    new_lines = [line for line in lines if message_substring not in line]
    
    with open("cron_temp", "w") as f:
        for line in new_lines:
            f.write(f'{line}\n')
    
    result = os.system("crontab cron_temp")
    os.remove("cron_temp")
    
    if result == 0:
        return json.dumps({"status": "success", "details": f"Removed tasks containing '{message_substring}'"})
    else:
        return json.dumps({"status": "error", "details": f"Failed to remove tasks. Crontab command returned non-zero exit code: {result}"})

def clear_all_cron_tasks():
    print("[cron_manager.py] clear_all_cron_tasks called.")
    result = os.system("crontab -r")
    if result == 0:
        return json.dumps({"status": "success", "details": "All cron tasks cleared."})
    else:
        return json.dumps({"status": "error", "details": f"Failed to clear all cron tasks. Crontab command returned non-zero exit code: {result}"})

def list_cron_tasks():
    return os.popen('crontab -l').read()

