from flask import Flask, request, jsonify
import message_handler

app = Flask(__name__)

@app.route("/process_message", methods=["POST"])
def process_message():
    data = request.json
    message = data.get("message")
    chat_id = data.get("chat_id")
    source = data.get("source")
    print(f"[api.py] Received message for processing: message='{message}', chat_id='{chat_id}', source='{source}'")
    response = message_handler.handle_message(message, chat_id, source)
    print(f"[api.py] Sending response: {response}")
    return jsonify({"response": response})

if __name__ == "__main__":
    print("[api.py] Starting Flask API on port 5000...")
    app.run(port=5000)
