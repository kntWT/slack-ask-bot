from dotenv import load_dotenv
import os

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_USER_ID = os.getenv("SLACK_BOT_USER_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DB_HOST = os.getenv("MYSQL_OUTSIDE_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")
