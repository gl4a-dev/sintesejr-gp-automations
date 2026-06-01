import logging

from core.logging import configure_logging
from core.exceptions import GoogleAPIError

from services.google.client import GoogleClient

from automations.tests.test_admin import run as run_admin
from automations.tests.test_docs import run as run_docs
from automations.tests.test_gmail import run as run_gmail
from automations.tests.test_sheets import run as run_sheets


configure_logging(level=logging.INFO, save_to_file=True)

def main():
    try:
        client = GoogleClient()

        #run_admin(client)
        run_docs(client)
        run_gmail(client)
        run_sheets(client)

    except GoogleAPIError as e:
        logging.exception(f"Error on execution: {e}")


if __name__ == "__main__":
    main()