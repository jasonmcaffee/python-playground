class Message:
    def __init__(self, message_text: str, raw_chatgpt_chat_completion_response=None):
        self.message_text = message_text
        self.raw_chatgpt_chat_completion_response = raw_chatgpt_chat_completion_response
