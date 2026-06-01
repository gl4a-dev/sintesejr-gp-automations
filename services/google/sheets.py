from typing import Any, cast
from googleapiclient.errors import HttpError
from services.google.service import GoogleService

from core.exceptions import GoogleSheetsError
from core.retry import retry_google_api
from core.google_scopes import GOOGLE_SCOPES
from core.settings import GOOGLE_OAUTH_TOKEN_FILE
from models.sheets import Spreadsheet
from services.google.types.sheets import GoogleSheetsServiceProtocol


class GoogleSheetsAPI(GoogleService):
    @property
    def service(self) -> GoogleSheetsServiceProtocol:
        return cast(
            GoogleSheetsServiceProtocol,
            super().service
        )

    @property
    def service_name(self) -> str:
        return "sheets"

    @property
    def version(self) -> str:
        return "v4"

    @property
    def scopes(self) -> list[str]:
        return GOOGLE_SCOPES
    
    @property
    def token_file(self) -> str:
        return str(GOOGLE_OAUTH_TOKEN_FILE)

    @retry_google_api
    def create_spreadsheet(self, title:str) -> Spreadsheet:
        if not title:
            raise ValueError("title can't be empty")

        try:
            spreadsheet_body = {
                "properties": {
                    "title": title
                }
            }

            result = self.service.spreadsheets().create(body=spreadsheet_body).execute()
            spreadsheet = Spreadsheet(
                id=result["spreadsheetId"],
                title=title
            )

            self.logger.info(
                "Spreadsheet created",
                extra={
                    "spreadsheet_id": spreadsheet.id,
                    "title": title
                }
            )

            return spreadsheet

        except HttpError as e:
            self.logger.exception("Error to create file")

            raise GoogleSheetsError(f"Error to create file: {e}") from e

    @retry_google_api
    def write_range(self, spreadsheet_id:str, range_name:str, values:list[list[Any]]) -> None:
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id can't be empty")

        if not range_name:
            raise ValueError("range_name can't be empty")

        if not values:
            raise ValueError("values can't be empty")

        try:
            body = {
                "values": values
            }

            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()

            self.logger.info(
                "Spreadsheet range updated",
                extra={
                    "spreadsheet_id": spreadsheet_id,
                    "range_name": range_name,
                    "rows_count": len(values)
                }
            )

        except HttpError as e:
            self.logger.exception("Error to write data")
            raise GoogleSheetsError(f"Error to write data: {e}") from e

    @retry_google_api
    def read_range( self, spreadsheet_id:str, range_name:str) -> list[list[Any]]:
        if not spreadsheet_id:
            raise ValueError("spreadsheet_id can't be empty")

        if not range_name:
            raise ValueError("range_name can't be empty")

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                )
                .execute()
            )

            values = result.get("values", [])

            self.logger.info(
                "Spreadsheet range read",
                extra={
                    "spreadsheet_id": spreadsheet_id,
                    "range_name": range_name,
                    "rows_count": len(values)
                }
            )

            return values

        except HttpError as e:
            self.logger.exception("Error to read data")
            raise GoogleSheetsError(f"Error to read data {e}") from e