from services.google.client import GoogleClient

if __name__ == "__main__":
    client = GoogleClient()
    client.drive.list_files()