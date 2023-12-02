from projects.chatgpt.models.Message import Message


class MessageFactory:
    @staticmethod
    def create_message_from_chatgpt_response(response):
        choices = response.choices
        choice = choices[0]
        gpt_message = choice['message']
        role = gpt_message['role']
        message_text = gpt_message['content']
        tool_calls = None
        finish_reason = None
        if 'tool_calls' in gpt_message:
            tool_calls = gpt_message['tool_calls']
        if 'finish_reason' in choice:
            finish_reason = choice['finish_reason']
        message = Message(message_text=message_text, role=role, raw_chatgpt_chat_completion_response=response,
                          tool_calls=tool_calls)
        return message

    @staticmethod
    def create_message_from_user_question(question: str):
        return Message(role="user", message_text=question)

    @staticmethod
    def create_system_prompt_message(system_prompt: str):
        return Message(role="system", message_text=system_prompt)
