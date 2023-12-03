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

    # determines if the function exists in the service.
    @abstractmethod
    def does_function_exist(self, function_name: str):
        pass

    # calls the function in the service, passing the arguments string, which should be json.
    # e.g. {param1: "1234", param2: "abc"}
    @abstractmethod
    def call_function(self, function_name: str, arguments: str):
        pass

    # Retrieves the list of tools/functions which are sent to chatgpt to describe the functions it's allowed to call.
    @abstractmethod
    def get_tools(self):
        pass
