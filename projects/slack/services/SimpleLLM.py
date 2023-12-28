import time

import openai

from projects.slack.config.Config import config
from projects.slack.models.SimpleStreamInferenceCallable import (SimpleStreamInferenceCallable, LLMTextReceivedCallable,
                                                                 LLMResponseCompletedCallable)


class SimpleLLM:
    def __init__(self):
        secret_key = config.get_open_ai_secret_key()
        openai.api_key = secret_key

    def stream_inference(self, prompt: str, handle_on_text_received: LLMTextReceivedCallable,
                         handle_response_complete: LLMResponseCompletedCallable) -> None:
        start_time_seconds = time.time()
        print(f"asking chatgpt: {prompt}")
        stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # "text-davinci-003",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that answers questions accurately, without making up facts."},
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )
        for output in stream:
            choices = output['choices']
            choice = choices[0]
            delta = choice['delta']
            if 'content' in delta:
                text = delta['content']
                handle_on_text_received(text)
                # print(delta['content'], end='')
        # handle_on_text_received(None, True)
        handle_response_complete()
        # print()
        print(f"answer received in {time.time() - start_time_seconds} seconds.")

    def get_simple_stream_inference_callable(self) -> SimpleStreamInferenceCallable:
        return lambda prompt, handle_on_text_received, handle_response_complete: (
            self.stream_inference(prompt, handle_on_text_received, handle_response_complete))
