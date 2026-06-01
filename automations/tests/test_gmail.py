import datetime as dt

from services.google.client import GoogleClient
from automations_config.tests_config import RECEIVER_EMAIL_ADDRESS

def run(client: GoogleClient):
    client.gmail.send_email(
        to=[RECEIVER_EMAIL_ADDRESS],
        subject=f"Email Teste - {dt.datetime.now()}",
        body=f"""
        <h2>Email Teste</h2>
        <p>Esse é um email de teste</p>
        """,
        html=True
    )