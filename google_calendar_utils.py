import os.path
import uuid
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# The path to your service account key file, loaded from environment variable or defaults to 'credentials.json'
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"] # Use calendar scope for full access

def get_calendar_service_service_account():
    """Authenticates using a service account and returns a Google Calendar API service object."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("calendar", "v3", credentials=creds)
    return service

def start_watching_calendar(service, calendar_id, webhook_url):
    """Starts watching a Google Calendar for events.
    Returns a dictionary containing 'id' (channel ID) and 'resourceId'."""
    request_body = {
        "id": str(uuid.uuid4()), # A unique ID for this notification channel
        "type": "web_hook",
        "address": webhook_url
    }
    return service.events().watch(calendarId=calendar_id, body=request_body).execute()

def stop_watching_calendar(service, channel_id, resource_id):
    """Stops watching a Google Calendar."""
    request_body = {
        "id": channel_id,
        "resourceId": resource_id
    }
    return service.channels().stop(body=request_body).execute()

def get_calendar_event(service, calendar_id, event_id):
    """Retrieves a specific calendar event."""
    return service.events().get(calendarId=calendar_id, eventId=event_id).execute()

if __name__ == "__main__":
    try:
        service = get_calendar_service_service_account()
        # Example: List the first 10 events on the primary calendar
        print("Getting the next 10 events from primary calendar")
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure your service account JSON file is correctly placed and the GOOGLE_APPLICATION_CREDENTIALS environment variable is set if it's not 'credentials.json'.")
    except Exception as e:
        print(f"An error occurred: {e}")
