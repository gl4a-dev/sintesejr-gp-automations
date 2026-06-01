from typing import Any
from typing import Protocol


class GmailExecuteProtocol(Protocol):
    def execute(self) -> dict[str, Any]:
        ...

class GmailMessagesProtocol(Protocol):
    def send(self, userId:str, body:dict[str, Any]) -> GmailExecuteProtocol:
        ...

class GmailUsersProtocol(Protocol):
    def messages(self) -> GmailMessagesProtocol:
        ...


class GoogleGmailServiceProtocol(Protocol):
    def users(self) -> GmailUsersProtocol:
        ...