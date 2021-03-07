# Bitbar Gmail Notifier
Bitbar plugin that displays recent emails and notifies on new messages.
Uses oauth2, which avoids the "less secure apps" problem when using basic auth.

## Dependencies
- `realpath`

## Setup
1. Clone the repo somewhere.
2. `python3 -m venv env`
3. `source env/bin/activate`
4. `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
5. Store `credentials.json` in `bitbar-gmail-notifier-secrets`
    - Enable Gmail API in Cloud Platform. Easy link here - click the button and save `credentials.json`: https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the
    - Otherwise manually create a project and save credentials
6. Symlink `bitbar-gmail-notifier.30s.sh` into your bitbar plugins folder.

## Config
- Config is in `bitbar-gmail-notifier-impl.py`.