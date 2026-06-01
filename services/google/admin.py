import string
import secrets
from typing import cast
from datetime import datetime
from zoneinfo import ZoneInfo
from googleapiclient.errors import HttpError

from core.google_scopes import GOOGLE_SCOPES 
from core.exceptions import GoogleAdminError
from core.retry import retry_google_api
from core.settings import GOOGLE_OAUTH_TOKEN_FILE
from models.admin import GoogleUser, CreatedGoogleUser
from services.google.service import GoogleService
from services.google.types.admin import GoogleAdminServiceProtocol


class GoogleAdminAPI(GoogleService):
    @property
    def service(self) -> GoogleAdminServiceProtocol:
        return cast(
            GoogleAdminServiceProtocol,
            super().service
        )

    @property
    def service_name(self) -> str:
        return "admin"

    @property
    def version(self) -> str:
        return "directory_v1"

    @property
    def scopes(self) -> list[str]:
        return GOOGLE_SCOPES
    
    @property
    def token_file(self) -> str:
        return str(GOOGLE_OAUTH_TOKEN_FILE)
    

    def _generate_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))
    
    @retry_google_api
    def create_user(self, first_name: str, last_name: str, primary_email: str, recovery_email: str, org_unit_path: str = "/") -> CreatedGoogleUser:
        try:
            temporary_password = self._generate_password()
            body = {
                "name": {"givenName": first_name, "familyName": last_name},
                "primaryEmail": primary_email,
                "password": temporary_password,
                "recoveryEmail": recovery_email,
                "changePasswordAtNextLogin": True,
                "orgUnitPath": org_unit_path,
            }

            created_user = self.service.users().insert(body=body).execute()

            self.logger.info(f"User created: {primary_email}")

            return CreatedGoogleUser(
                id=created_user["id"],
                name=f"{first_name} {last_name}",
                primary_email=created_user["primaryEmail"],
                temporary_password=temporary_password,
                recovery_email=recovery_email
            )

        except HttpError as e:
            raise GoogleAdminError(f"Error to create user: {e}") from e

    @retry_google_api
    def list_users(self, max_results: int = 100) -> list[GoogleUser]:
        try:
            response = self.service.users().list(
                domain="sintesejr.com.br",
                maxResults=max_results
            ).execute()

            users = []

            for user_data in (response.get("users", [])):
                name = user_data.get("name", {})

                emails = []
                usp_email = user_data.get("recoveryEmail") if user_data.get("recoveryEmail", "").endswith("@usp.br") else None

                for email_data in user_data.get("emails", []):
                    address = email_data.get("address")
                    if not address:
                        continue

                    
                    if usp_email == None and address.endswith("@usp.br"):
                        usp_email = address

                    emails.append(address)

                    aliases = user_data.get("aliases", [])

                creation_time = None
                creation_time_raw = user_data.get("creationTime")
                if creation_time_raw:
                    creation_time = datetime.fromisoformat(creation_time_raw.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Sao_Paulo"))

                users.append(
                    GoogleUser(
                        id=user_data["id"],
                        primary_email=user_data["primaryEmail"],
                        given_name=name.get("givenName", ""),
                        family_name=name.get("familyName",""),
                        suspended=user_data.get("suspended", False),
                        recovery_email=user_data.get("recoveryEmail"),
                        emails=emails,
                        aliases=aliases,
                        usp_email=usp_email,
                        creation_time=creation_time
                    )
                )

            self.logger.info(f"{len(users)} users founded")
            return users

        except HttpError as e:
            raise GoogleAdminError(f"Error to list users: {e}") from e