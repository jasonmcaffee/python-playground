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
            result = {
                "function_name": function_name,
                "arguments": arguments,
                # data needed for subsequent calls to chatgpt
                "metadata": {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": None,  # todo: populate this once the function has been executed.
                },
            }
            results.append(result)
    return results


def get_tool_data(tool_data_dict):
    def decorator(func):
        # Attach the tool data to the function
        func.tool_data = tool_data_dict
        return func

    return decorator
