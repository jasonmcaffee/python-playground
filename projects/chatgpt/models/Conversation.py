from typing import List, Tuple, Set, Dict

from projects.chatgpt.models.Message import Message


class Conversation:
    def __init__(self, conversation_id: str, messages: List[Message]):
        self.conversation_id = conversation_id
        self.messages = messages

    def add_message(self, message: Message):
        self.messages.append(message)
