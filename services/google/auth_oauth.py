import os.path
from typing import Any
from typing import Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from core.exceptions import GoogleAuthenticationError
from core.settings import GOOGLE_OAUTH_CLIENT_FILE, GOOGLE_OAUTH_TOKEN_FILE


class GoogleOAuthAuthenticator:
    def __init__(self, credentials_file:str = str(GOOGLE_OAUTH_CLIENT_FILE)):
        self.credentials_file = credentials_file
        self._credentials_cache: dict[str, Credentials] = {}
        self._services_cache: dict[str, Any] = {}

    def authenticate(self, scopes:Sequence[str], token_file:str = str(GOOGLE_OAUTH_TOKEN_FILE)) -> Credentials:
        if token_file in self._credentials_cache:
            return self._credentials_cache[token_file]

        try:
            creds = None
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, scopes)

            if not creds or not creds.valid:

                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())

                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, scopes)
                    creds = flow.run_local_server(port=0)

                with open(token_file, "w") as token:
                    token.write(creds.to_json())

            self._credentials_cache[token_file] = creds
            return creds

        except Exception as e:
            raise GoogleAuthenticationError(f"Error on Google Authentication: {e}") from e

    def build_service(self, service_name:str, version:str, scopes:Sequence[str], token_file:str = str(GOOGLE_OAUTH_TOKEN_FILE)) -> Any:
        cache_key = f"{service_name}:{version}:{token_file}"
        if cache_key in self._services_cache:
            return self._services_cache[cache_key]

        creds = self.authenticate(scopes=scopes, token_file=token_file)
        service = build(service_name, version, credentials=creds, cache_discovery=False)
        self._services_cache[cache_key] = service

        return service