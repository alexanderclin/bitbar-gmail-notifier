import os
import os.path
import pickle
import time
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

################################################################################
# START CONFIG

# Number of results. Default is 10
RESULTS = 10

# Query for what messages to show and/or notify on. Default is "in:inbox"
QUERY = "in:inbox"

# Show notifications. Default is True
SHOW_NOTIFICATIONS = True

# Notify on messages newer than NOTIFICATION_THRESHOLD seconds.
# Should be equal to the plugin refresh rate. Default is 30
NOTIFICATION_THRESHOLD_SECONDS = 30

# Location of the directory where credentials.json and token will be stored.
# Default is os.path.join(os.path.dirname(os.path.realpath(__file__)), "bitbar-gmail-notifier-secrets")
SECRETS_DIRECTORY = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "bitbar-gmail-notifier-secrets"
)

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


def main():
    print("✉")
    print("---")

    # Get credentials
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(SECRETS_DIRECTORY, "token.pickle")):
        with open(os.path.join(SECRETS_DIRECTORY, "token.pickle"), "rb") as token:
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
            creds = flow.run_local_server(port=0, authorization_prompt_message="")

        # Save the credentials for the next run
        with open(os.path.join(SECRETS_DIRECTORY, "token.pickle"), "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    # Call the Gmail API
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=RESULTS, q=QUERY)
        .execute()
    )
    messages = results.get("messages", [])
    if not messages:
        print("No messages found.")
    else:
        batch = service.new_batch_http_request()

        def message_callback(id, email, exception):
            # Generate link
            link = f'https://mail.google.com/mail/#inbox/{email["id"]}'

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
                SHOW_NOTIFICATIONS
                and int(time.time()) - email_timestamp <= NOTIFICATION_THRESHOLD_SECONDS
            ):
                notify(snippet, subject_header, from_header)

            # Print out emails
            email_formatted_time = datetime.fromtimestamp(email_timestamp).strftime(
                "%b %d"
            )
            print(
                f"{email_formatted_time} ￨ {subject_header} | length=50 href={link} font=Monaco"
            )
            print(f"--{from_header} ￨ {email_formatted_time} | href={link}")
            print(f"--{subject_header} | length=50 href={link}")
            print("-----")
            print(f"--{snippet} | length=50 href={link}")

        for message_id in messages:
            batch.add(
                service.users().messages().get(userId="me", id=message_id["id"]),
                callback=message_callback,
            )

        batch.execute()

    print("---")
    print(f"Refresh | refresh=true")


if __name__ == "__main__":
    main()
