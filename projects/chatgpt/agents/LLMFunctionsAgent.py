import json
import time
import uuid
from typing import List, Tuple, Set, Dict

from projects.chatgpt.models.Conversation import Conversation
from projects.chatgpt.utils.function_calling_utils import get_function_calls_details_from_llm_response, get_tool_data

system_prompt = "You are a helpful assistant that answers questions accurately, without making up facts."
model = "gpt-3.5-turbo"


# Agent which:
# - provides an inference function which accepts a question to send to chatgpt and responds with the answer.
# - maintains a conversation, which is a collection of messages that have been sent to and received from chatgpt.
# - determines if chatgpt has requested that a local function has been called.
# - executes the local function and sends the result to chatgpt (via conversation messages)
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

    def inference(self, question=None, conversation=None, start_time_seconds=None):
        # start a new conversation if needed, which tracks all messages to and from chatgpt
        conversation = self.ensure_conversation_exists(conversation)

        # measure how long it takes to complete
        start_time_seconds = start_time_seconds if start_time_seconds is not None else time.time()

        # initial call will have a user question, but some calls will be to pass local function results back to chatgpt.
        conversation.add_user_question_to_messages_if_applicable(question)

        # get all messages in the conversation history to pass to chatgpt
        messages = conversation.get_messages_in_chatgpt_format()
        # print(f"sending messages: {messages}")

        # call chatgpt
        response = self.openai.ChatCompletion.create(model=model, messages=messages, tools=self.tools)
        # print(response)

        # add the response to our conversation.  we may need to pass it back to chatgpt if a function is called.
        conversation.add_chatgpt_response_to_messages(response)

        # call local functions
        # the results of all called functions will be stored in metadata.content
        functions_details = self.call_appropriate_function_based_on_llm_response(response)
        # add response of local functions to messages and recursively call chatgpt again so the response is passed.
        if functions_details is not None:
            conversation.add_functions_details_as_messages_in_conversation(functions_details)
            # print('recursively calling inference to pass back the results of the functions called')
            return self.inference(question=None, conversation=conversation, start_time_seconds=start_time_seconds)

        # return the answer as text
        return self.handle_chatgpt_completed_response(response, conversation, start_time_seconds)

    # if chatgpt response with 'stop', print out the answer and return it.
    def handle_chatgpt_completed_response(self, response, conversation, start_time_seconds):
        if self.get_finish_reason_from_chatgpt_response(response) == 'stop':
            last_message = conversation.get_last_message()
            print(f"chatgpt response: \n {last_message.message_text}")
            print(f"answer received in {time.time() - start_time_seconds} seconds.")
            return last_message.message_text

    # help determine if chatgpt has completed "stop"
    def get_finish_reason_from_chatgpt_response(self, response):
        choices = response['choices']
        choice = choices[0]
        finish_reason = choice['finish_reason']
        return finish_reason

    def ensure_conversation_exists(self, conversation: Conversation):
        if conversation is None:
            conversation = Conversation(conversation_id=str(uuid.uuid4()), system_prompt=system_prompt)
        return conversation

    def call_appropriate_function_based_on_llm_response(self, llm_response):
        # determine if chatgpt is asking to call any local functions
        functions = get_function_calls_details_from_llm_response(llm_response)
        if functions is None:
            return None

        # call each local function chatgpt has asked to call.
        # store the result of the function into function_details.function_result
        for function_details in functions:
            function_name = function_details.function_name
            arguments = function_details.arguments
            function_to_call = self.function_map.get(function_name)
            if function_to_call is not None:
                function_result = function_to_call(arguments)
                function_details.function_result = function_result
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
        text_response = json.dumps(response)
        print(f"get_user_details is returning: {text_response}")
        return text_response