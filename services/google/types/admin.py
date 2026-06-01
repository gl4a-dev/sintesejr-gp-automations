from typing import Any
from typing import Protocol


class AdminExecuteProtocol(Protocol):
    def execute(self) -> dict[str, Any]:
        ...

class AdminUsersProtocol(Protocol):
    def list(self, domain: str, maxResults: int = 100) -> AdminExecuteProtocol:
        ...

    def insert(self, body: dict[str, Any]) -> AdminExecuteProtocol:
        ...


class GoogleAdminServiceProtocol(Protocol):
    def users(self) -> AdminUsersProtocol:
        ...