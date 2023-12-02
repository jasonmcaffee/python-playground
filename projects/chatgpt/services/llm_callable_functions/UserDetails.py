import json

from projects.chatgpt.decorators.chatgpt_tool_data import chatgpt_tool_data


class UserDetails:
    def __init__(self):
        print('')
        # so we can call the function
        self.function_map = {
            "get_user_details": self.get_user_details
        }

        # list of function metadata sent to chatgpt so it knows which functions it can call.
        self.tools = [
            self.get_user_details.tool_data
        ]

    def does_function_exist(self, function_name: str):
        function_to_call = self.function_map.get(function_name)
        return function_to_call is not None

    def call_function(self, function_name: str, arguments: str):
        function_to_call = self.function_map.get(function_name)
        if function_to_call is not None:
            function_result = function_to_call(arguments)
            return function_result

    @chatgpt_tool_data({
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
