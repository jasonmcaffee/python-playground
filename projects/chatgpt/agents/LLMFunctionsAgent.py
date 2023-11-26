import json
import time
from projects.chatgpt.utils.function_calling_utils import get_function_calls_details_from_llm_response, get_tool_data


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
        print(f'tools are {self.tools}')

    def function_call_prompt(self, question):
        start_time_seconds = time.time()
        print(f"asking chatgpt: {question}")
        response = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that answers questions accurately, without making up facts."},
                {"role": "user", "content": question}
            ],
            tools=self.tools
        )
        print(response)

        self.call_appropriate_function_based_on_llm_response(response)

        print(f"answer received in {time.time() - start_time_seconds} seconds.")

    def call_appropriate_function_based_on_llm_response(self, llm_response):
        functions = get_function_calls_details_from_llm_response(llm_response)
        for function_details in functions:
            function_name = function_details.get('function_name')
            arguments = function_details.get('arguments')
            function_to_call = self.function_map.get(function_name)
            if function_to_call is not None:
                function_to_call(arguments)

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

#
# _tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_user_details",
#             "description": "Retrieves information for a user based on the combination of their first and last names.  It returns information about the user's age, location, and profession.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "first_name": {
#                         "type": "string",
#                         "description": "First name of the user to get details of."
#                     },
#                     "last_name": {
#                         "type": "string",
#                         "description": "Last name of the user to get details of."
#                     }
#                 },
#                 "required": ["first_name", "last_name"]
#             }
#         },
#
#     },
# ]
