import io
from typing import cast
from googleapiclient.errors import HttpError
from services.google.service import GoogleService
from googleapiclient.http import MediaIoBaseDownload

from core.exceptions import GoogleDriveError
from core.retry import retry_google_api
from core.google_scopes import GOOGLE_SCOPES
from core.settings import GOOGLE_OAUTH_TOKEN_FILE
from models.drive import DriveFile
from services.google.types.drive import GoogleDriveServiceProtocol


class GoogleDriveAPI(GoogleService):
    @property
    def service(self) -> GoogleDriveServiceProtocol:
        return cast(
            GoogleDriveServiceProtocol,
            super().service
        )
    
    @property
    def service_name(self) -> str:
        return "drive"

    @property
    def version(self) -> str:
        return "v3"

    @property
    def scopes(self) -> list[str]:
        return GOOGLE_SCOPES

    @property
    def token_file(self) -> str:
        return str(GOOGLE_OAUTH_TOKEN_FILE)

    @retry_google_api
    def list_files(self, page_size:int = 10) -> list[DriveFile]:

        try:
            results = (
                self.service.files()
                .list(
                    pageSize=page_size,
                    fields="files(id, name, mimeType, webViewLink)"
                )
                .execute()
            )

            files = [
                DriveFile(
                    id=file["id"],
                    name=file["name"],
                    mime_type=file["mimeType"],
                    web_view_link=file["webViewLink"]
                )
                for file in results.get("files", [])
            ]

            self.logger.info(
                "Files listed",
                extra={
                    "count": len(files)
                }
            )

            return files

        except HttpError as e:
            self.logger.exception(
                "Erro ao listar arquivos"
            )

            raise GoogleDriveError(
                f"Erro ao listar arquivos: {e}"
            ) from e
        
    @retry_google_api
    def copy_file(self, file_id:str, new_name:str) -> DriveFile:
        if not file_id:
            raise ValueError("file_id can't be empty")

        if not new_name:
            raise ValueError("new_name can't be empty")

        try:
            body = {
                "name": new_name
            }

            result = (
                self.service.files()
                .copy(
                    fileId=file_id,
                    body=body,
                    fields=("id, name, mimeType, webViewLink")
                )
                .execute()
            )

            copied_file = DriveFile(
                id=result["id"],
                name=result["name"],
                mime_type=result["mimeType"],
                web_view_link=result["webViewLink"]
            )

            self.logger.info(
                "File copied",
                extra={
                    "source_file_id": file_id,
                    "copied_file_id": copied_file.id
                }
            )

            return copied_file

        except HttpError as e:
            self.logger.exception("Error on file copy")

            raise GoogleDriveError(f"Error on file copy: {e}") from e
        
    @retry_google_api
    def move_file_to_folder(self, file_id:str, folder_id:str) -> None:

        if not file_id:
            raise ValueError("file_id can't be empty")

        if not folder_id:
            raise ValueError("folder_id can't be empty")

        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="parents"
            ).execute()

            previous_parents = ",".join(file.get("parents", []))

            self.service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields="id, parents"
            ).execute()

            self.logger.info(
                "File moved",
                extra={
                    "file_id": file_id,
                    "previous_parents": previous_parents,
                    "new_parent": folder_id
                }
            )

        except HttpError as e:
            self.logger.exception("Error to move file")
            raise GoogleDriveError(f"Error to move file: {e}") from e
        
    @retry_google_api
    def export_file(self, file_id:str, mime_type:str) -> bytes:
        if not file_id:
            raise ValueError("file_id can't be empty")

        if not mime_type:
            raise ValueError("mime_type can't be empty")

        try:
            request = (
                self.service.files()
                .export(
                    fileId=file_id,
                    mimeType=mime_type
                )
            )

            file_buffer = io.BytesIO()

            downloader = MediaIoBaseDownload(file_buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            file_content = file_buffer.getvalue()

            self.logger.info(
                "File exported",
                extra={
                    "file_id": file_id,
                    "mime_type": mime_type,
                    "size_bytes": len(file_content)
                }
            )

            return file_content

        except HttpError as e:
            self.logger.exception("Error to export file")
            raise GoogleDriveError(f"Error to export file: {e}") from e    

    @retry_google_api
    def delete_file(self, file_id:str) -> None:
        if not file_id:
            raise ValueError("file_id can't be empty")

        try:
            (
                self.service.files()
                .delete(
                    fileId=file_id
                )
                .execute()
            )

            self.logger.info(
                "File deleted",
                extra={
                    "file_id": file_id
                }
            )

        except HttpError as e:
            self.logger.exception("Error to delete file")
            raise GoogleDriveError(f"Error to delete file: {e}") from e
            
    @retry_google_api
    def create_folder(self, name: str) -> DriveFile:
        if not name:
            raise ValueError("name can't be empty")

        try:
            body = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder"
            }

            result = (
                self.service.files()
                .create(
                    body=body,
                    fields=(
                        "id, name, mimeType, webViewLink"
                    )
                )
                .execute()
            )

            created_folder = DriveFile(
                id=result["id"],
                name=result["name"],
                mime_type=result["mimeType"],
                web_view_link=result.get("webViewLink")
            )

            self.logger.info(
                "Folder created",
                extra={
                    "folder_id": created_folder.id,
                    "folder_name": created_folder.name
                }
            )

            return created_folder

        except HttpError as e:
            self.logger.exception("Error to create folder")
            raise GoogleDriveError(f"Error to create folder: {e}") from e
        
    @retry_google_api
    def move_folder_to_folder(self, folder_id: str, parent_folder_id: str) -> None:

        if not folder_id:
            raise ValueError("folder_id can't be empty")

        if not parent_folder_id:
            raise ValueError("parent_folder_id can't be empty")

        try:
            folder = (
                self.service.files()
                .get(
                    fileId=folder_id,
                    fields="parents"
                )
                .execute()
            )

            previous_parents = ",".join(
                folder.get("parents", [])
            )

            (
                self.service.files()
                .update(
                    fileId=folder_id,
                    addParents=parent_folder_id,
                    removeParents=previous_parents,
                    fields="id, parents"
                )
                .execute()
            )

            self.logger.info(
                "Folder moved",
                extra={
                    "folder_id": folder_id,
                    "previous_parents": previous_parents,
                    "new_parent": parent_folder_id
                }
            )

        except HttpError as e:
            self.logger.exception("Error to move folder")
            raise GoogleDriveError(f"Error to move folder: {e}") from e