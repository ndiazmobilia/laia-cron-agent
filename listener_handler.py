from openai import OpenAI
import config
import cron_manager
import memory
import json

client = OpenAI(api_key=config.OPENAI_API_KEY)

def add_cron_job(crontab, message):
    print(f"[listener_handler.py] add_cron_job called with crontab: '{crontab}' and message: '{message}'")
    crontab = crontab.strip('"') # Remove quotes
    print(f"[listener_handler.py] Stripped crontab: '{crontab}'")
    chat_id = memory.load_chat_id()
    if not chat_id:
        print("[listener_handler.py] Error: chat_id not found.")
        return "I can't schedule tasks without a chat ID. Please send a message to the bot first."

    # Escape double quotes in the message for the shell command
    escaped_message = message.replace("\"", "\\\"")
    command = f"/mnt/c/Users/ndiaz/PycharmProjects/laia-cron-agent/.venv/bin/python3 /mnt/c/Users/ndiaz/PycharmProjects/laia-cron-agent/notifier.py \"{escaped_message}\" {chat_id}"
    print(f"[listener_handler.py] Generated command for cron: {command}")
    
    result = cron_manager.add_cron_task(command, crontab)
    print(f"[listener_handler.py] Result from cron_manager: {result}")
    return result

def handle_message(message, chat_id, assistant):
    print(f"[listener_handler.py] handle_message called for chat_id: {chat_id} with message: '{message}'")
    print(f"[listener_handler.py] Using assistant ID: {assistant.id}")

    print("[listener_handler.py] Creating new thread...")
    thread = client.beta.threads.create()
    print(f"[listener_handler.py] Thread created with ID: {thread.id}")

    print("[listener_handler.py] Adding message to thread...")
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    print("[listener_handler.py] Message added to thread.")

    print("[listener_handler.py] Creating run...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"[listener_handler.py] Run created with ID: {run.id}")

    print("[listener_handler.py] Waiting for run to complete...")
    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"[listener_handler.py] Run status: {run.status}")

    if run.status == 'requires_action':
        print(f"[listener_handler.py] Run requires action. Tool calls: {run.required_action.submit_tool_outputs.tool_calls}")
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"[listener_handler.py] Tool call: {function_name}({arguments})")
            if function_name == 'add_cron_job':
                if 'crontab' not in arguments or 'message' not in arguments:
                    return "I'm sorry, I couldn't schedule the task. Please provide a valid time and message."
                output = add_cron_job(arguments['crontab'], arguments['message'])
                print(f"[listener_handler.py] Tool output: {output}")
                tool_outputs.append({
                    'tool_call_id': tool_call.id,
                    'output': output
                })
        
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        print("[listener_handler.py] Submitted tool outputs.")
        # Wait for the run to complete after submitting tool outputs
        while run.status in ['queued', 'in_progress']:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"[listener_handler.py] Run status: {run.status}")

    if run.status == "failed":
        error_message = f"[listener_handler.py] Run failed. Error code: {run.last_error.code}, Message: {run.last_error.message}"
        print(error_message)
        return f"An error occurred while processing your request: {run.last_error.message}"

    print("[listener_handler.py] Run completed. Retrieving messages...")
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    response_content = ""
    if messages.data and messages.data[0].content:
        for content_block in messages.data[0].content:
            if content_block.type == 'text':
                response_content += content_block.text.value
    
    print(f"[listener_handler.py] Assistant response: {response_content}")
    return response_content