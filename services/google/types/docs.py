from typing import Any
from typing import Protocol


class DocsExecuteProtocol(Protocol):
    def execute(self) -> dict[str, Any]:
        ...


class DocsCreateProtocol(Protocol):
    def create(self, body:dict[str, Any]) -> DocsExecuteProtocol:
        ...


class DocsGetProtocol(Protocol):
    def get(self, documentId:str) -> DocsExecuteProtocol:
        ...


class DocsBatchUpdateProtocol(Protocol):
    def batchUpdate(
        self,
        documentId: str,
        body: dict[str, Any]
    ) -> DocsExecuteProtocol:
        ...


class DocsDocumentsProtocol(DocsCreateProtocol, DocsGetProtocol, DocsBatchUpdateProtocol, Protocol):
    pass


class GoogleDocsServiceProtocol(Protocol):
    def documents(self) -> DocsDocumentsProtocol:
        ...