from dataclasses import dataclass

@dataclass
class EmailAttachment:
    filename: str
    content: bytes
    mime_type: str