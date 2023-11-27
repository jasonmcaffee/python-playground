class Message:
    def __init__(self, message_text: str, role: str = "user", raw_chatgpt_chat_completion_response=None):
        self.role = role
        self.message_text = message_text
        self.raw_chatgpt_chat_completion_response = raw_chatgpt_chat_completion_response

    def to_chatgpt_format(self):
        return {
            "role": self.role,
            "content": self.message_text,
        }
