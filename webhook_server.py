from flask import Flask, request, Response
import json
import os
from telegram_utils import send_telegram_message
from google_calendar_utils import get_calendar_service_service_account, get_calendar_event

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receives notifications from Google Calendar API."""
    if not request.data:
        return Response(status=204)  # No content

    try:
        # Google Calendar API sends notifications via HTTP headers
        channel_id = request.headers.get('X-Goog-Channel-ID')
        resource_id = request.headers.get('X-Goog-Resource-ID')
        resource_state = request.headers.get('X-Goog-Resource-State')
        resource_uri = request.headers.get('X-Goog-Resource-URI')
        message_number = request.headers.get('X-Goog-Message-Number')

        print(f"Received Calendar Notification:\n"\
              f"  Channel ID: {channel_id}\n"\
              f"  Resource ID: {resource_id}\n"\
              f"  Resource State: {resource_state}\n"\
              f"  Resource URI: {resource_uri}\n"\
              f"  Message Number: {message_number}")

        service = get_calendar_service_service_account()
        calendar_id = 'primary' # Assuming primary calendar for now

        if resource_state == 'exists':
            # Event exists or was updated
            event = get_calendar_event(service, calendar_id, resource_id)
            summary = event.get('summary', 'No Summary')
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            end_time = event['end'].get('dateTime', event['end'].get('date'))

            notification_message = f"<b>Calendar Event Updated/Created:</b>\n\n"\
                                   f"<b>Summary:</b> {summary}\n"\
                                   f"<b>Start:</b> {start_time}\n"\
                                   f"<b>End:</b> {end_time}\n"\
                                   f"Resource ID: {resource_id}"
            send_telegram_message(notification_message)

        elif resource_state == 'not_exists':
            # Event was deleted
            notification_message = f"<b>Calendar Event Deleted:</b>\n\n"\
                                   f"Resource ID: {resource_id}"
            send_telegram_message(notification_message)

        else:
            # Other states like 'sync'
            notification_message = f"<b>Calendar Sync Notification:</b>\n\n"\
                                   f"Resource State: {resource_state}\n"\
                                   f"Resource ID: {resource_id}"
            send_telegram_message(notification_message)

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return Response(status=200) # Still acknowledge to prevent retries

    return Response(status=200)

if __name__ == "__main__":
    # This is for local testing only. In production, use a Gunicorn server.
    app.run(port=8080, debug=True)
