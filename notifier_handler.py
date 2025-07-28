from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def handle_message(message, chat_id, assistant):
    print(f"[notifier_handler.py] handle_message called for chat_id: {chat_id} with message: '{message}'")
    print(f"[notifier_handler.py] Using assistant ID: {assistant.id}")

    print("[notifier_handler.py] Creating new thread...")
    thread = client.beta.threads.create()
    print(f"[notifier_handler.py] Thread created with ID: {thread.id}")

    print("[notifier_handler.py] Adding message to thread...")
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    print("[notifier_handler.py] Message added to thread.")

    print("[notifier_handler.py] Creating run...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"[notifier_handler.py] Run created with ID: {run.id}")

    print("[notifier_handler.py] Waiting for run to complete...")
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print(f"[notifier_handler.py] Run status: {run.status}")

        if run.status == "failed":
            error_message = f"[notifier_handler.py] Run failed. Error code: {run.last_error.code}, Message: {run.last_error.message}"
            print(error_message)
            return f"An error occurred while processing your request: {run.last_error.message}"

    print("[notifier_handler.py] Run completed. Retrieving messages...")
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    response_content = ""
    if messages.data and messages.data[0].content:
        for content_block in messages.data[0].content:
            if content_block.type == 'text':
                response_content += content_block.text.value
    
    print(f"[notifier_handler.py] Assistant response: {response_content}")
    return response_content