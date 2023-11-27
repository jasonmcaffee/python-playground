class Message:
    def __init__(self, message_text: str, role: str = "user", tool_call_id: str = None, function_name: str = None, raw_chatgpt_chat_completion_response=None):
        self.function_name = function_name
        self.tool_call_id = tool_call_id
        self.role = role
        self.message_text = message_text
        self.raw_chatgpt_chat_completion_response = raw_chatgpt_chat_completion_response

    # def to_chatgpt_format(self):
    #     return {
    #         "role": self.role,
    #         "content": self.message_text,
    #         "tool_call_id": self.tool_call_id,
    #         "name": self.function_name,
    #     }

    def to_chatgpt_format(self):
        return {
            key: value for key, value in [
                ("role", self.role),
                ("content", self.message_text),
                ("tool_call_id", self.tool_call_id),
                ("name", self.function_name)
            ] if value is not None
        }
