from typing import List, Tuple, Set, Dict

from projects.chatgpt.models.Message import Message


class Conversation:
    def __init__(self, conversation_id: str, messages: List[Message] = None):
        if messages is None:
            messages: List[Message] = []
        self.conversation_id = conversation_id
        self.messages = messages

    def add_message(self, message: Message):
        self.messages.append(message)

    def get_messages_in_chatgpt_format(self):
        # return list(map(lambda message: message.to_chatgpt_format(), self.messages))
        result = []
        for message in self.messages:
            chatgpt_message = message.to_chatgpt_format()
            result.append(chatgpt_message)

        return result

    def get_last_message(self):
        if len(self.messages) == 0:
            return None
        last_message = self.messages[-1]
        return last_message
