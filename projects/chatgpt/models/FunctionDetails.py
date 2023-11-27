from projects.chatgpt.models.Message import Message


class FunctionMetadata:
    def __init__(self):
        print('')


class FunctionDetails:
    def __init__(self, function_name: str, arguments: str, function_result: str = None, tool_call_id: str = None):
        self.function_name = function_name
        self.arguments = arguments
        self.function_result = function_result
        self.tool_call_id = tool_call_id

    def to_message(self):
        return Message(message_text=self.function_result, role="tool", tool_call_id=self.tool_call_id, function_name=self.function_name)

    def to_chat_gpt_message(self):
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "name": self.function_name,
            "content": self.function_result,
        }
