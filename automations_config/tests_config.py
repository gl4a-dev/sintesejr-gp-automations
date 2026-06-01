import os
from dotenv import load_dotenv


load_dotenv()

AUTOMATION_TESTS_FOLDER_ID = os.getenv("AUTOMATION_TESTS_FOLDER_ID")
DOCS_TEMPLATE_ID = os.getenv("DOCS_TEMPLATE_ID")
RECEIVER_EMAIL_ADDRESS = os.getenv("RECEIVER_EMAIL_ADDRESS")