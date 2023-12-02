from typing import List, Tuple, Set, Dict

from projects.chatgpt.factories.MessageFactory import MessageFactory
from projects.chatgpt.models.FunctionDetails import FunctionDetails
from projects.chatgpt.models.Message import Message


class Conversation:
    def __init__(self, conversation_id: str,  system_prompt: str, messages: List[Message] = None):
        if messages is None:
            messages: List[Message] = []
        self.conversation_id = conversation_id
        self.messages = messages
        self.system_prompt = system_prompt
        self.ensure_system_prompt_message_exists()

    def ensure_system_prompt_message_exists(self):
        if len(self.messages) == 0:
            message = MessageFactory.create_system_prompt_message(system_prompt=self.system_prompt)
            self.add_message(message)

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

    def add_user_question_to_messages_if_applicable(self, question: str):
        if question is None:
            return
        message = MessageFactory.create_message_from_user_question(question)
        self.add_message(message)

    # converts the result from a function call to a message and adds it to the conversation history.
    def add_functions_details_as_messages_in_conversation(self, functions_details: List[FunctionDetails]):
        if functions_details is None:
            return
        for function_details in functions_details:
            message = function_details.to_message()
            self.add_message(message)
