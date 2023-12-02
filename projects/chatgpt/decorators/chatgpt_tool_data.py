
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
def chatgpt_tool_data(tool_data_dict):
    def decorator(func):
        # Attach the tool data to the function
        func.tool_data = tool_data_dict
        return func

    return decorator