from typing import Callable

# when we receive text from an LLM
LLMTextReceivedCallable = Callable[[str], None]
# when we receive notification that an LLM response has completed
LLMResponseCompletedCallable = Callable[[], None]
# AI bot communicates to an LLM through this abstraction
SimpleStreamInferenceCallable = Callable[[str, LLMTextReceivedCallable, LLMResponseCompletedCallable], None]
