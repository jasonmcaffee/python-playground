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

        # todo: reflection ran into issues: descriptor '__weakref__' for 'CallableFunctionServiceBase' objects doesn't apply to a 'UserDetails'
        # self._populate_function_map()
        # for name, method in inspect.getmembers(self, predicate=inspect.isfunction):
        #     # Bind the method to self
        #     bound_method = method.__get__(self, self.__class__)
        #     if hasattr(bound_method, 'tool_data'):
        #         self.function_map[name] = bound_method
        #         self.tools.append(bound_method.tool_data)
        # Populate function_map and tools with methods having the @chatgpt_tool_data decorator
        # for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
        #     if hasattr(method, 'tool_data'):
        #         self.function_map[name] = method
        #         self.tools.append(method.tool_data)

    # def _populate_function_map(self):
    #     for name, method in inspect.getmembers(self, predicate=inspect.isfunction):
    #         # Check if the method is defined in the current instance's class (or subclasses)
    #         if method.__qualname__.startswith(self.__class__.__qualname__):
    #             if hasattr(method, 'tool_data'):
    #                 # Add the method as an unbound function; it will be bound automatically when called
    #                 self.function_map[name] = method
    #                 self.tools.append(method.tool_data)

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
