from typing import Any
from typing import cast
from googleapiclient.errors import HttpError

from core.exceptions import GoogleDocsError
from core.google_scopes import GOOGLE_SCOPES
from core.retry import retry_google_api
from core.settings import GOOGLE_OAUTH_TOKEN_FILE
from models.docs import Document
from services.google.service import GoogleService
from services.google.types.docs import GoogleDocsServiceProtocol


class GoogleDocsAPI(GoogleService):
    @property
    def service(self) -> GoogleDocsServiceProtocol:
        return cast(
            GoogleDocsServiceProtocol,
            super().service
        )

    @property
    def service_name(self) -> str:
        return "docs"

    @property
    def version(self) -> str:
        return "v1"

    @property
    def scopes(self) -> list[str]:
        return GOOGLE_SCOPES

    @property
    def token_file(self) -> str:
        return str(GOOGLE_OAUTH_TOKEN_FILE)

    @retry_google_api
    def create_document(self, title:str) -> Document:
        if not title:
            raise ValueError("title can't be empty")

        try:
            body = {
                "title": title
            }

            result = (
                self.service.documents()
                .create(body=body)
                .execute()
            )

            document = Document(
                id=result["documentId"],
                title=result["title"],
                url=(
                    f"https://docs.google.com/document/d/"
                    f"{result['documentId']}/edit"
                )
            )

            self.logger.info(
                "Document created",
                extra={
                    "document_id": document.id
                }
            )

            return document

        except HttpError as e:
            self.logger.exception("Erro ao criar documento")
            raise GoogleDocsError("Erro ao criar documento") from e

    @retry_google_api
    def get_document(self, document_id:str) -> Document:
        if not document_id:
            raise ValueError("document_id can't be empty")

        try:
            result = (
                self.service.documents()
                .get(documentId=document_id)
                .execute()
            )

            document = Document(
                id=result["documentId"],
                title=result["title"],
                url=(
                    f"https://docs.google.com/document/d/"
                    f"{result['documentId']}/edit"
                )
            )

            self.logger.info(
                "Document retrieved",
                extra={
                    "document_id": document.id
                }
            )

            return document

        except HttpError as e:
            self.logger.exception("Error getting document")
            raise GoogleDocsError("Error getting document") from e

    @retry_google_api
    def batch_update(self, document_id:str, requests:list[dict[str, Any]]) -> None:
        if not document_id:
            raise ValueError("document_id can't be empty")

        if not requests:
            raise ValueError("requests can't be empty")

        try:
            body = {
                "requests": requests
            }

            (
                self.service.documents()
                .batchUpdate(
                    documentId=document_id,
                    body=body
                )
                .execute()
            )

            self.logger.info(
                "Document updated",
                extra={
                    "document_id": document_id,
                    "requests_count": len(requests)
                }
            )

        except HttpError as e:
            self.logger.exception("Error updating document")
            raise GoogleDocsError("Error updating document") from e

    def replace_text(self, document_id:str, replacements:dict[str, str]) -> None:
        if not replacements:
            raise ValueError("replacements can't be empty")

        requests = []

        for old_text, new_text in replacements.items():
            requests.append({
                "replaceAllText": {
                    "containsText": {
                        "text": old_text,
                        "matchCase": True
                    },
                    "replaceText": new_text
                }
            })

        self.batch_update(
            document_id=document_id,
            requests=requests
        )

        self.logger.info(
            "Text replaced",
            extra={
                "document_id": document_id,
                "replacements_count": len(replacements)
            }
        )