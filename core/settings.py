from pathlib import Path
import logging


BASE_DIR = Path(__file__).resolve().parent.parent

# Credentials
CREDENTIALS_DIR = BASE_DIR / "credentials"
OAUTH_CREDENTIALS_DIR = CREDENTIALS_DIR / "oauth"
GOOGLE_OAUTH_CLIENT_FILE = OAUTH_CREDENTIALS_DIR / "google_oauth_client.json"
GOOGLE_OAUTH_TOKEN_FILE = OAUTH_CREDENTIALS_DIR / "token_google.json"

# Log
LOG_LEVEL = logging.INFO
LOG_FILE = BASE_DIR / "app.log"