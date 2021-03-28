import json
import os
import os.path
import pickle
import time
from datetime import datetime
from functools import partial

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

################################################################################
# START CONFIG

# Location of the directory where credentials.json and token will be stored.
# Default is os.path.join(os.path.dirname(os.path.realpath(__file__)), "bitbar-gmail-notifier-secrets")
SECRETS_DIRECTORY = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "bitbar-gmail-notifier-secrets"
)

# User settings. Reads from SECRETS_DIRECTORY/config.json
# Format:
# {
#   "user@gmail.com": {
#       "results": int (Number of results. Default is 10),
#       "query": str (Query for what messages to show and/or notify on, like "in:inbox"),
#       "show_notifications": bool (Show notifications)
#   }
# }
with open(os.path.join(SECRETS_DIRECTORY, "config.json")) as f:
    USERS = json.load(f)

# Notify on messages newer than NOTIFICATION_THRESHOLD seconds.
# Should be equal to the plugin refresh rate. Default is 30
NOTIFICATION_THRESHOLD_SECONDS = 30

# END CONFIG
################################################################################

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def notify(display, title, subtitle):
    os.system(
        """
              osascript -e 'display notification "{}" with title "{}" subtitle "{}" sound name "Hero"'
              """.format(
            display, title, subtitle
        )
    )


# Replace "|" and "-" with similar looking characters.
def sanitize(string):
    return string.replace("|", "￨").replace("-", "−")


def get_service(user):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(SECRETS_DIRECTORY, f"{user}-token.pickle")):
        with open(
            os.path.join(SECRETS_DIRECTORY, f"{user}-token.pickle"), "rb"
        ) as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(SECRETS_DIRECTORY, "credentials.json"),
                SCOPES,
            )
            notify(f"Login with {user}", "Bitbar Gmail Notifier", "")
            creds = flow.run_local_server(
                port=0, authorization_prompt_message="", open_browser=True
            )

        # Save the credentials for the next run
        with open(
            os.path.join(SECRETS_DIRECTORY, f"{user}-token.pickle"), "wb"
        ) as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)
    return service


def message_callback(user, id, email, exception):
    # Generate link
    # https://stackoverflow.com/questions/38877956/get-direct-url-to-email-from-gmail-api-list-messages
    # https://webapps.stackexchange.com/questions/18959/can-i-form-a-direct-url-to-a-particular-gmail-account
    link = f'https://mail.google.com/mail/u/{user}/#all/{email["id"]}'
    link = (
        f"https://accounts.google.com/ServiceLogin?"
        f"service=mail&passive=true&Email={user}"
        f'&continue=https://mail.google.com/mail/u/{user}/%23all/{email["id"]}'
    )

    # Get headers
    from_header = "From"
    subject_header = "Subject"
    for header in email["payload"]["headers"]:
        if header["name"] == "From":
            from_header = header["value"]
        elif header["name"] == "Subject":
            subject_header = header["value"]

    # Create snippet
    snippet = f'{email["snippet"]}'

    # Sanitize
    from_header = sanitize(from_header)
    subject_header = sanitize(subject_header)
    snippet = sanitize(snippet)

    # Notify if needed
    email_timestamp = int(int(email["internalDate"]) / 1000)
    if (
        USERS[user]["show_notifications"]
        and int(time.time()) - email_timestamp <= NOTIFICATION_THRESHOLD_SECONDS
    ):
        notify(snippet, subject_header, from_header)

    # Print out emails
    email_formatted_time = datetime.fromtimestamp(email_timestamp).strftime("%b %d")
    print(f"{email_formatted_time} ￨ {subject_header} | length=50 href={link}")
    print(f"--{from_header} ￨ {email_formatted_time} | href={link}")
    print(f"--{subject_header} | length=50 href={link}")
    print("-----")
    print(f"--{snippet} | length=50 href={link}")


def main():
    print("✉")
    print("---")

    for user, _ in USERS.items():
        service = get_service(user)
        link = (
            f"https://accounts.google.com/ServiceLogin?"
            f"service=mail&passive=true&Email={user}"
            f"&continue=https://mail.google.com/mail/u/{user}"
        )
        print(f"{user} | href={link}")
        results = (
            service.users()
            .messages()
            .list(
                userId="me", maxResults=USERS[user]["results"], q=USERS[user]["query"]
            )
            .execute()
        )
        messages = results.get("messages", [])
        if not messages:
            print("No messages found.")
        else:
            batch = service.new_batch_http_request()
            for message_id in messages:
                batch.add(
                    service.users().messages().get(userId="me", id=message_id["id"]),
                    callback=partial(message_callback, user),
                )
            batch.execute()
        print("---")

    print(f"Refresh | refresh=true")


if __name__ == "__main__":
    main()
