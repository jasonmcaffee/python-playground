import time

import openai

from projects.slack.config.Config import config
from projects.slack.models.SimpleStreamInferenceCallable import (SimpleStreamInferenceCallable, LLMTextReceivedCallable,
                                                                 LLMResponseCompletedCallable)


class SimpleLLM:
    def __init__(self):
        secret_key = config.get_open_ai_secret_key()
        openai.api_key = secret_key

        self.client = openai.OpenAI(
            base_url="http://192.168.0.209:8080/v1",  # "THIS MUST BE 127.0.0.1, not localhost
            api_key="sk-no-key-required"
        )

    def stream_inference(self, prompt: str, handle_on_text_received: LLMTextReceivedCallable,
                         handle_response_complete: LLMResponseCompletedCallable) -> None:
        start_time_seconds = time.time()
        print(f"asking chatgpt: {prompt}")
        system_message = f"""
        You are an all knowing Artificial Intelligence who provides well thought out answers to questions and tasks.
        You are vigilant in ensuring you do not write gibberish, such as a long sequence of seemingly random characters, or words or phrases that repeat.  
        If you notice that you are writing gibberish, stop doing so, apologize, and stop responding.
        """
        completion = self.client.chat.completions.create(
            model="llama-3",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            stream=True,  # Whether to stream the response or return the full response at once
            max_tokens=2000,  # The maximum number of tokens to generate in the completion
            temperature=0.5,  # The temperature of the model, controlling the randomness of the output
            top_p=1.0,  # The nucleus sampling parameter, controlling the diversity of the output
            n=1,  # The number of completions to generate
            stop=None,  # A list of stop sequences to stop the completion at
            presence_penalty=0.0,  # The penalty for generating tokens that appear in the prompt
            frequency_penalty=0.0,  # The penalty for generating tokens that appear frequently in the prompt
            logit_bias={},  # A dictionary of token IDs and associated biases to apply to the logits
        )

        # print(completion.choices[0].message)
        for chunk in completion:
            text = chunk.choices[0].delta.content
            print(text, end="")
            handle_on_text_received(text)
                # print(delta['content'], end='')
        # handle_on_text_received(None, True)
        handle_response_complete()
        # print()
        print(f"answer received in {time.time() - start_time_seconds} seconds.")

    def get_simple_stream_inference_callable(self) -> SimpleStreamInferenceCallable:
        return lambda prompt, handle_on_text_received, handle_response_complete: (
            self.stream_inference(prompt, handle_on_text_received, handle_response_complete))
