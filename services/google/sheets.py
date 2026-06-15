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
    def create_spreadsheet(self, title:str, sheet_names:list[str] | None = None) -> Spreadsheet:
        """
        Cria uma nova planilha no Google Sheets.

        Opcionalmente, é possível definir os nomes das abas iniciais.
        Caso nenhuma aba seja informada, o Google criará automaticamente
        uma aba padrão.

        :param title:
            Título atribuído à planilha.
            Exemplo: "Processo Seletivo 2026"

        :param sheet_names:
            Lista com os nomes das abas a serem criadas.
            Exemplo:
                ["Inscrições", "Entrevistas", "Resultados"]

            Se None, uma aba padrão será criada pelo Google.

        :return:
            Metadados da planilha criada.

        :raises ValueError:
            Se o título estiver vazio.

        :raises GoogleSheetsError:
            Se ocorrer erro na API do Google Sheets.
        """

        if not title:
            raise ValueError("title can't be empty")

        try:
            spreadsheet_body = {
                "properties": {
                    "title": title
                }
            }

            if sheet_names:
                spreadsheet_body["sheets"] = [
                    {"properties": {"title": sheet_name}}
                    for sheet_name in sheet_names if sheet_name
                ]

            result = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet = Spreadsheet(id=result["spreadsheetId"], title=title)

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
    def create_sheet(self, spreadsheet_id: str, title: str) -> None:
        """
        Cria uma nova aba em uma planilha existente do Google Sheets.

        :param spreadsheet_id:
            Identificador da planilha.
            Exemplo: "1AbCdEfGhIjKlMnOpQrStUvWxYz"

        :param title:
            Nome da nova aba.
            Exemplo: "Avaliações"

        :return:
            None.

        :raises ValueError:
            Se o identificador da planilha ou o título estiverem vazios.

        :raises GoogleSheetsError:
            Se ocorrer erro na API do Google Sheets.
        """

        if not spreadsheet_id:
            raise ValueError("spreadsheet_id can't be empty")

        if not title:
            raise ValueError("title can't be empty")

        try:
            body = {
                "requests": [{
                    "addSheet": { "properties": { "title": title } }
                }]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            self.logger.info(
                "Sheet created",
                extra={
                    "spreadsheet_id": spreadsheet_id,
                    "sheet_title": title
                }
            )

        except HttpError as e:
            self.logger.exception("Error to create sheet")
            raise GoogleSheetsError(f"Error to create sheet: {e}") from e

    @retry_google_api
    def write_range(self, spreadsheet_id:str, range_name:str, values:list[list[Any]]) -> None:
        """
        Escreve valores em um intervalo específico de uma planilha
        utilizando A1 notation.

        Os valores existentes no intervalo informado serão sobrescritos.

        :param spreadsheet_id:
            Identificador da planilha.
            Exemplo: "1AbCdEfGhIjKlMnOpQrStUvWxYz"

        :param range_name:
            Intervalo no formato A1 notation.
            Exemplos:
                - "Avaliações!A1:D10"
                - "Sheet1!B2:C5"

        :param values:
            Valores a serem escritos na planilha.
            Exemplo:
            [
                ["Nome", "Setor"],
                ["Ricardo", "Tecnologia"]
            ]

        :return:
            None.

        :raises ValueError:
            Se algum parâmetro obrigatório estiver vazio.

        :raises GoogleSheetsError:
            Se ocorrer erro na API do Google Sheets.
        """

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
        """
        Lê os valores de um intervalo específico de uma planilha
        utilizando A1 notation.

        :param spreadsheet_id:
            Identificador da planilha.
            Exemplo: "1AbCdEfGhIjKlMnOpQrStUvWxYz"

        :param range_name:
            Intervalo no formato A1 notation.
            Exemplos:
                - "Avaliações!A1:D10"
                - "Resultados!A2:B20"

        :return:
            Lista bidimensional contendo os valores encontrados no
            intervalo solicitado.

        :raises ValueError:
            Se o identificador da planilha ou o intervalo estiverem vazios.

        :raises GoogleSheetsError:
            Se ocorrer erro na API do Google Sheets.
        """
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