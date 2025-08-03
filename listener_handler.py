from openai import OpenAI
import config
import cron_manager
import memory
import json
import re
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(api_key=config.OPENAI_API_KEY)

PROJECT_ROOT = os.getenv('PROJECT_ROOT', '/mnt/c/Users/ndiaz/PycharmProjects/laia-cron-agent')

def add_cron_job(crontab, message):
    logging.info(f"add_cron_job called with crontab: '{crontab}' and message: '{message}'")
    crontab = crontab.strip('"') # Remove quotes
    logging.info(f"Stripped crontab: '{crontab}'")
    chat_id = memory.load_chat_id()
    if not chat_id:
        logging.error("Error: chat_id not found.")
        return "I can't schedule tasks without a chat ID. Please send a message to the bot first."

    # Escape double quotes in the message for the shell command
    escaped_message = message.replace("\"", "\\\"")
    command = f"{PROJECT_ROOT}/.venv/bin/python3 {PROJECT_ROOT}/notifier.py \"{escaped_message}\" {chat_id}"
    logging.info(f"Generated command for cron: {command}")
    
    result = cron_manager.add_cron_task(command, crontab)
    logging.info(f"Result from cron_manager: {result}")
    return result

def list_reminders():
    logging.info("list_reminders called.")
    cron_tasks = cron_manager.list_cron_tasks()
    if not cron_tasks:
        return "No reminders scheduled."

    reminders = []
    for line in cron_tasks.splitlines():
        # Example line: * * * * * /usr/bin/python3 /mnt/c/Users/ndiaz/PycharmProjects/laia-cron-agent/notifier.py "Hello" 12345
        parts = line.split(' ', 5) # Split into 6 parts: time (5 parts) and command (1 part)
        if len(parts) == 6:
            time_part = " ".join(parts[:5])
            command_part = parts[5]
            # Extract the message from the command part
            # The command is expected to be: /path/to/notifier.py "message" chat_id
            # We need to find the string between the first and second double quotes after notifier.py
            match = re.search(r'notifier\.py \"(.*?)\" \d+', command_part)
            if match:
                message = match.group(1)
                reminders.append(f"- At {time_part}: \"{message}\"")
            else:
                reminders.append(f"- {line} (unparsable message)")
        else:
            reminders.append(f"- {line} (unparsable format)")
    return "Your scheduled reminders:\n" + "\n".join(reminders)

def delete_reminder(message_substring):
    logging.info(f"delete_reminder called with message_substring: '{message_substring}'")
    return cron_manager.remove_cron_task(message_substring)

def delete_all_reminders():
    logging.info("delete_all_reminders called.")
    return cron_manager.clear_all_cron_tasks()

def add_one_time_reminder(time, message):
    """Schedules a one-time reminder using the at command."""
    logging.info(f"add_one_time_reminder called with time: '{time}' and message: '{message}'")
    chat_id = memory.load_chat_id()
    if not chat_id:
        logging.error("Error: chat_id not found.")
        return "I can't schedule tasks without a chat ID. Please send a message to the bot first."

    escaped_message = message.replace("\"", "\\\"")
    command = f"{PROJECT_ROOT}/.venv/bin/python3 {PROJECT_ROOT}/notifier.py \"{escaped_message}\" {chat_id}"
    logging.info(f"Generated command for at: {command}")
    
    result = cron_manager.add_at_job(command, time)
    logging.info(f"Result from cron_manager: {result}")
    return result

def handle_message(message, chat_id, assistant):
    logging.info(f"handle_message called for chat_id: {chat_id} with message: '{message}'")
    logging.info(f"Using assistant ID: {assistant.id}")

    logging.info("Creating new thread...")
    thread = client.beta.threads.create()
    logging.info(f"Thread created with ID: {thread.id}")

    logging.info("Adding message to thread...")
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    logging.info("Message added to thread.")

    logging.info("Creating run...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    logging.info(f"Run created with ID: {run.id}")

    logging.info("Waiting for run to complete...")
    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        logging.info(f"Run status: {run.status}")

    if run.status == 'requires_action':
        logging.info(f"Run requires action. Tool calls: {run.required_action.submit_tool_outputs.tool_calls}")
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            logging.info(f"Tool call: {function_name}({arguments})")
            if function_name == 'add_cron_job':
                if 'crontab' not in arguments or 'message' not in arguments:
                    output = "I'm sorry, I couldn't schedule the task. Please provide a valid time and message."
                else:
                    output = add_cron_job(arguments['crontab'], arguments['message'])
            elif function_name == 'add_one_time_reminder':
                if 'time' not in arguments or 'message' not in arguments:
                    output = "I'm sorry, I couldn't schedule the one-time task. Please provide a valid time and message."
                else:
                    output = add_one_time_reminder(arguments['time'], arguments['message'])
            elif function_name == 'list_reminders':
                output = list_reminders()
            elif function_name == 'delete_reminder':
                if 'message_substring' not in arguments:
                    output = "I'm sorry, I couldn't delete the reminder. Please provide a message substring."
                else:
                    output = delete_reminder(arguments['message_substring'])
            elif function_name == 'delete_all_reminders':
                output = delete_all_reminders()
            else:
                output = f"Unknown tool call: {function_name}"
            
            logging.info(f"Tool output: {output}")
            tool_outputs.append({
                'tool_call_id': tool_call.id,
                'output': output
            })
        
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        logging.info("Submitted tool outputs.")
        # Wait for the run to complete after submitting tool outputs
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            logging.info(f"Run status: {run.status}")
            if run.status not in ['queued', 'in_progress']:
                break

    if run.status == "failed":
        error_message = f"Run failed. Error code: {run.last_error.code}, Message: {run.last_error.message}"
        logging.error(error_message)
        return f"An error occurred while processing your request: {run.last_error.message}"

    logging.info("Run completed. Retrieving messages...")
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    response_content = ""
    if messages.data and messages.data[0].content:
        for content_block in messages.data[0].content:
            if content_block.type == 'text':
                response_content += content_block.text.value
    
    logging.info(f"Assistant response: {response_content}")
    return response_content
