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

    def inference(self, question=None, conversation: Conversation = Conversation(conversation_id=str(uuid.uuid4()))):
        start_time_seconds = time.time()

        # add the initial system prompt as the first message.
        if len(conversation.messages) == 0:
            conversation.add_message(Message(role="system", message_text=system_prompt))

        # add a message for question, if supplied.
        if question is not None:
            conversation.add_message(Message(role="user", message_text=question))

        messages = conversation.get_messages_in_chatgpt_format()
        print(f"sending messages: {messages}")

        response = self.openai.ChatCompletion.create(
            model=model,
            messages=messages,
            tools=self.tools
        )
        print(response)

        # the results of all called functions will be stored in metadata.content
        functions_details = self.call_appropriate_function_based_on_llm_response(response)

        # todo: the function_details response must be added to the conversation.
        # InvalidRequestError: Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls'.

        if functions_details is not None:
            print('todo: pass function results back to chat completion')  # todo: pass function results
            for function_details in functions_details:
                message = function_details.to_message()
                conversation.add_message(message)

            print('recursively calling inference to pass back the results of the functions called')
            self.inference(question=None, conversation=conversation)
        else:
            self.add_response_to_messages(raw_chatgpt_chat_completion_response=response,
                                          functions_details=functions_details, conversation=conversation)

        print(f"answer received in {time.time() - start_time_seconds} seconds.")

    def add_question_to_messages(self, question: str, conversation: Conversation):
        message = Message(message_text=question, role="user")
        conversation.add_message(message)

    def add_response_to_messages(self, raw_chatgpt_chat_completion_response, functions_details, conversation):
        message = Message(message_text="", raw_chatgpt_chat_completion_response=raw_chatgpt_chat_completion_response)
        conversation.add_message(message)

    def call_appropriate_function_based_on_llm_response(self, llm_response):
        functions = get_function_calls_details_from_llm_response(llm_response)
        for function_details in functions:
            function_name = function_details.function_name
            arguments = function_details.arguments
            function_to_call = self.function_map.get(function_name)
            if function_to_call is not None:
                function_result = function_to_call(arguments)
                function_details.function_result = function_result
                # chat gpt will refer to the result
                # function_details['metadata']['content'] = function_result
                # print('added function metadata content')
        return functions
        # for function_details in functions:
        #     function_name = function_details.get('function_name')
        #     arguments = function_details.get('arguments')
        #     function_to_call = self.function_map.get(function_name)
        #     if function_to_call is not None:
        #         function_result = function_to_call(arguments)
        #         # chat gpt will refer to the result
        #         function_details['metadata']['content'] = function_result
        #         print('added function metadata content')
        # return functions

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
        text_response = json.dumps(response)
        print(f"get_user_details is returning: {text_response}")
        return text_response
