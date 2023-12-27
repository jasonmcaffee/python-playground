import time
import os
from dotenv import load_dotenv
import openai
from typing import Callable

load_dotenv()
max_tokens = 4092

secret_key = os.getenv('OPEN_AI_SECRET_KEY')
openai.api_key = secret_key


class SimpleChatGPT:
    def stream_prompt(self, question: str, handle_on_text_received: Callable[[str], None], handle_response_complete: Callable[[], None]):
        start_time_seconds = time.time()
        print(f"asking chatgpt: {question}")
        stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # "text-davinci-003",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that answers questions accurately, without making up facts."},
                {"role": "user", "content": question}
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
