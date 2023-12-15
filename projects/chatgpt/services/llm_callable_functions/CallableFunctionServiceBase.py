import inspect
from abc import abstractmethod, ABC


# Defines functions required for services which house functions that chatgpt is allowed to call
class CallableFunctionServiceBase(ABC):
    def __init__(self):
        print('')
        # dictionary of functions decorated with @chatgpt_tool_data.  e.g. {"get_user_details": function(){...} }
        self.function_map = {}
        # list of all tool_data retrieved from functions decorated with @chatgpt_tool_data.
        self.tools = []
        # iterate over every function in the child class and
        self.initialize_function_map_and_tools()

    # Iterates over every method in the child class and evaluates whether it uses the @chatgpt_tool_data decorator.
    # add the tool_data to the tools list, which is referenced when Agents describe local functions to chatgpt, so
    # that chatgpt can choose whether to indicate that a function should be called with arguments X, Y, Z
    def initialize_function_map_and_tools(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, 'tool_data'):
                # print(f'---- found function with tool_data: {name}')
                self.function_map[name] = method
                self.tools.append(method.tool_data)

    # Used by the agent when handling a tools response from ChatGPT.  The agent searches through services, finding the
    # appropriate function to call.
    def does_function_exist(self, function_name: str):
        function_to_call = self.function_map.get(function_name)
        # print(f'does_function exist: {function_name} is {function_to_call is not None}')
        return function_to_call is not None

    # Used by the agent when handling a tools response from ChatGPT.  The agent will pass a function_name string and
    # json arguments as a string.
    def call_function(self, function_name: str, arguments: str):
        function_to_call = self.function_map.get(function_name)
        # print(f'calling function {function_name}')
        if function_to_call is not None:
            function_result = function_to_call(arguments)
            # print(f'function result: {function_result}')
            return function_result

    # returns the list of tool_data entries, which were obtained by iterating over each method with a @chatgpt_tool_data
    # decorator.
    def get_tools(self):
        return self.tools
