from abc import ABC, abstractmethod
from typing import Sequence
from typing import Any

from services.google.auth_oauth import GoogleOAuthAuthenticator

from core.logging import get_logger


class GoogleService(ABC):
    def __init__(self, authenticator:GoogleOAuthAuthenticator):
        self.authenticator = authenticator

        self.logger = get_logger(
            self.__class__.__name__
        )

        self._service = None

    @property
    def service(self) -> Any:
        if self._service is None:
            self._service = (
                self.authenticator.build_service(
                    service_name=self.service_name,
                    version=self.version,
                    scopes=self.scopes,
                    token_file=self.token_file
                )
            )

        return self._service

    @property
    @abstractmethod
    def service_name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def scopes(self) -> Sequence[str]:
        pass

    @property
    @abstractmethod
    def token_file(self) -> str:
        pass