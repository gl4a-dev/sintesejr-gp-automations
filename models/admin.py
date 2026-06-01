from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class GoogleUser:
    id: str
    primary_email: str
    given_name: str
    family_name: str
    suspended: bool
    creation_time: datetime | None
    recovery_email: str | None = None
    usp_email: str | None = None
    emails: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

@dataclass
class CreatedGoogleUser:
    id: str
    name: str
    primary_email: str
    temporary_password: str
    recovery_email: str