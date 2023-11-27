# If the llm response indicates that a local function should be called, this function will parse
# the function names and associated parameters into an array of objects:
# [
#   {
#       "function_name": "get_user_details",
#       "arguments": '{"first_name": "Jason", "last_name": "McAffee"}',
#       "metadata": {
#           "tool_call_id": tool_call.id,
#           "role": "tool",
#           "name": function_name,
#           "content": None,  # todo: populate this once the function has been executed.
#        },
#   }
# ]
from projects.chatgpt.models.FunctionDetails import FunctionDetails


def get_function_calls_details_from_llm_response(response):
    # print('get_function_calls_details_from_llm_response called for response:')
    # print(response)
    response_message = response.choices[0].message
    tool_calls = response_message.get('tool_calls')
    results = None
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            # result = {
            #     "function_name": function_name,
            #     "arguments": arguments,
            #     # data needed for subsequent calls to chatgpt
            #     "metadata": {
            #         "tool_call_id": tool_call.id,
            #         "role": "tool",
            #         "name": function_name,
            #         "content": None,  # todo: populate this once the function has been executed.
            #     },
            # }
            result = FunctionDetails(function_name=function_name, arguments=arguments, tool_call_id=tool_call.id)
            results.append(result)
    return results


# decorator so we can use attributes to describe the function behavior in a way in which chatgpt understands.
# Example:
#     @get_tool_data({
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
#     })
#     def get_user_details(self, args):
#         ...
def get_tool_data(tool_data_dict):
    def decorator(func):
        # Attach the tool data to the function
        func.tool_data = tool_data_dict
        return func

    return decorator
