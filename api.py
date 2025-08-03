from flask import Flask, request, jsonify
import message_handler
import logging

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route("/process_message", methods=["POST"])
def process_message():
    data = request.json
    message = data.get("message")
    chat_id = data.get("chat_id")
    source = data.get("source")
    app.logger.info(f"Received message for processing: message='{message}', chat_id='{chat_id}', source='{source}'")
    response = message_handler.handle_message(message, chat_id, source)
    app.logger.info(f"Sending response: {response}")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.logger.setLevel(logging.INFO)
    app.logger.info("Starting Flask API on port 5000...")
    app.run(port=5000)
