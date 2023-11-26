import json

from projects.chatgpt.utils.function_calling_utils import get_function_calls_details_from_llm_response


class LLMFunctionsAgent:
    def __init__(self):
        print('init')
        self.function_map = {
            "get_user_details": self.get_user_details
        }

    def call_appropriate_function_based_on_llm_response(self, llm_response):
        functions = get_function_calls_details_from_llm_response(llm_response)
        for function_details in functions:
            function_name = function_details.get('function_name')
            arguments = function_details.get('arguments')
            function_to_call = self.function_map.get(function_name)
            if function_to_call is not None:
                function_to_call(arguments)

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
