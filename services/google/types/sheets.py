from typing import Any
from typing import Protocol


class SheetsExecuteProtocol(Protocol):
    def execute(self) -> dict[str, Any]:
        ...

class SheetsValuesProtocol(Protocol):
    def get(self, spreadsheetId:str, range:str) -> SheetsExecuteProtocol:
        ...

    def update(self, spreadsheetId:str, range:str, valueInputOption:str, body:dict[str, Any]) -> SheetsExecuteProtocol:
        ...


class SheetsSpreadsheetsProtocol(Protocol):
    def create(self, body:dict[str, Any]) -> SheetsExecuteProtocol:
        ...

    def values(self) -> SheetsValuesProtocol:
        ...


class GoogleSheetsServiceProtocol(Protocol):
    def spreadsheets(self) -> SheetsSpreadsheetsProtocol:
        ...