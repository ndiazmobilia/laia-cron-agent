from openai import OpenAI
import config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(api_key=config.OPENAI_API_KEY)

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
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        logging.info(f"Run status: {run.status}")

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