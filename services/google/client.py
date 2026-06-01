from services.google.auth_oauth import GoogleOAuthAuthenticator
from services.google.drive import GoogleDriveAPI
from services.google.docs import GoogleDocsAPI
from services.google.sheets import GoogleSheetsAPI
from services.google.gmail import GoogleGmailAPI
from services.google.admin import GoogleAdminAPI

class GoogleClient:
    def __init__(self, authenticator: (GoogleOAuthAuthenticator | None) = None):
        self.authenticator = (authenticator or GoogleOAuthAuthenticator())
        self.drive = GoogleDriveAPI(self.authenticator)
        self.docs = GoogleDocsAPI(self.authenticator)
        self.sheets = GoogleSheetsAPI(self.authenticator)
        self.gmail = GoogleGmailAPI(self.authenticator)
        self.admin = GoogleAdminAPI(self.authenticator)