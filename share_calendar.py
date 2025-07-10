import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# Load environment variables from .env file
load_dotenv()

# The path to your service account key file, loaded from environment variable or defaults to 'credentials.json'
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service_service_account():
    """Authenticates using a service account and returns a Google Calendar API service object."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build("calendar", "v3", credentials=creds)
    return service

def get_service_account_email():
    service_account_email = os.getenv("SERVICE_ACCOUNT_EMAIL")
    if not service_account_email:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            creds_data = json.load(f)
            service_account_email = creds_data.get('client_email')
    return service_account_email

def list_calendar_acls(calendar_id: str):
    try:
        service = get_calendar_service_service_account()
        acl_rules = service.acl().list(calendarId=calendar_id).execute()
        print(f"ACL rules for calendar {calendar_id}:")
        for rule in acl_rules.get('items', []):
            print(f"  Scope: {rule.get('scope', {}).get('type')}, Value: {rule.get('scope', {}).get('value')}, Role: {rule.get('role')}")
    except Exception as e:
        print(f"Error listing ACLs: {e}")

def share_calendar_with_user(user_email: str, role: str = "reader"):
    """Shares the service account's primary calendar with a specified user."""
    try:
        service = get_calendar_service_service_account()
        service_account_email = get_service_account_email()

        if not service_account_email:
            print("Error: Could not determine service account email.")
            return

        print(f"Attempting to share calendar ID: {service_account_email} with {user_email} as {role}.")

        rule = {
            'scope': {
                'type': 'user',
                'value': user_email,
            },
            'role': role,
        }

        created_rule = service.acl().insert(calendarId=service_account_email, body=rule).execute()
        print(f"Successfully shared calendar with {user_email} with role {role}.")
        print(f"Rule ID: {created_rule['id']}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    personal_email = "laialubens@gmail.com"
    service_account_email = get_service_account_email()
    if service_account_email:
        list_calendar_acls(service_account_email)
        share_calendar_with_user(personal_email, role="reader")
    else:
        print("Could not determine service account email. Cannot proceed.")