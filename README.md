# Bitbar Gmail Notifier
Bitbar plugin that displays recent emails and notifies on new messages. You can also click on entries to go to the email in your browser.

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

## Running the Plugin
1. Add `config.json` to the secrets folder (default `bitbar-gmail-notifier-secrets`). Formatting details are in `bitbar-gmail-notifier-impl.py`
2. When the plugin first start it will open Sign In pages for each user you added. Make sure to sign in with the same order as what you have in `config.json`

## Config
- Config is in `bitbar-gmail-notifier-impl.py`.