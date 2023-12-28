import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None  # singleton implementation

    def __new__(cls):  # singleton implementation
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def get_open_ai_secret_key(self):
        return os.getenv('OPEN_AI_SECRET_KEY')

    def get_slack_api_token(self):
        return os.getenv('SLACK_API_TOKEN')

    def get_ai_bot_user_slack_handle(self):
        return '<@U06ANF43Q57>'

    def get_edit_slack_message_after_n_chars_received_from_llm(self):
        return 20


# Singleton implementation
config = Config()
