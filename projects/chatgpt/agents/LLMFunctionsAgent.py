import json
import time
import uuid

from projects.chatgpt.models.Conversation import Conversation
from projects.chatgpt.models.Message import Message
from projects.chatgpt.utils.function_calling_utils import get_function_calls_details_from_llm_response, get_tool_data

system_prompt = "You are a helpful assistant that answers questions accurately, without making up facts."
model = "gpt-3.5-turbo"


# create a new instance for every new conversation
class LLMFunctionsAgent:
    def __init__(self, openai):
        print('init')
        self.function_map = {
            "get_user_details": self.get_user_details
        }
        # list of function metadata sent to chatgpt so it knows which functions it can call.
        self.tools = [
            self.get_user_details.tool_data
        ]
        self.openai = openai

    def inference(self, question, conversation: Conversation = Conversation(conversation_id=str(uuid.uuid4()))):
        start_time_seconds = time.time()

        self.add_question_to_messages(question, conversation)

        response = self.openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            tools=self.tools
        )
        print(response)

        # the results of all called functions will be stored in metadata.content
        functions_details = self.call_appropriate_function_based_on_llm_response(response)

        self.add_response_to_messages(raw_chatgpt_chat_completion_response=response, functions_details=functions_details, conversation=conversation)
        print(f"answer received in {time.time() - start_time_seconds} seconds.")

    def add_question_to_messages(self, question: str, conversation: Conversation):
        message = Message(message_text=question)
        conversation.add_message(message)

    def add_response_to_messages(self, raw_chatgpt_chat_completion_response, functions_details, conversation):
        message = Message(message_text="", raw_chatgpt_chat_completion_response=raw_chatgpt_chat_completion_response)
        conversation.add_message(message)

    def call_appropriate_function_based_on_llm_response(self, llm_response):
        functions = get_function_calls_details_from_llm_response(llm_response)
        for function_details in functions:
            function_name = function_details.get('function_name')
            arguments = function_details.get('arguments')
            function_to_call = self.function_map.get(function_name)
            if function_to_call is not None:
                function_result = function_to_call(arguments)
                # chat gpt will refer to the result
                function_details['metadata']['content'] = function_result
                print('added function metadata content')
        return functions

    @get_tool_data({
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "Retrieves information for a user based on the combination of their first and last names.  It returns information about the user's age, location, and profession.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "First name of the user to get details of."
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Last name of the user to get details of."
                    }
                },
                "required": ["first_name", "last_name"]
            }
        },
    })
    def get_user_details(self, args):
        arguments = json.loads(args)
        print(
            f"get_user_details function called with arguments first_name: {arguments['first_name']}, last_name: {arguments['last_name']}")
        response = {
            "age": 44,
            "location": {
                "state": "Utah"
            },
            "profession": "Software Engineer"
        }
        return response
