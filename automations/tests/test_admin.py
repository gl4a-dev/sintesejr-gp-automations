from services.google.client import GoogleClient


def run(client: GoogleClient) -> None:
    users = client.admin.list_users(10)
    for user in users:
        print(f"{user.given_name} {user.family_name}: {user.primary_email}")