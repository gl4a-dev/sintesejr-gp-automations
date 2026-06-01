class GoogleAPIError(Exception):
    pass

class GoogleAuthenticationError(GoogleAPIError):
    pass

class GoogleSheetsError(GoogleAPIError):
    pass

class GoogleDriveError(GoogleAPIError):
    pass

class GoogleDocsError(GoogleAPIError):
    """Erro relacionado ao Google Docs."""
    pass

class GoogleGmailError(GoogleAPIError):
    """Erro relacionado ao Gmail."""
    pass

class GoogleAdminError(GoogleAPIError):
    """Erro relacionado ao Google Admin SDK."""
    pass