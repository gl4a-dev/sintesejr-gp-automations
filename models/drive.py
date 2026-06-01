from dataclasses import dataclass

@dataclass
class DriveFile:
    id: str
    name: str
    mime_type: str
    web_view_link: str