import time
import openai
max_tokens = 4092

with open('projects/slack/openai-secret-key.txt', 'r') as file:
    secret_key = file.read().strip()

openai.api_key = secret_key

class SimpleChatGPT:
    def stream_prompt(self, question, handle_on_text_received):
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
                handle_on_text_received(text, False)
                # print(delta['content'], end='')
        handle_on_text_received(None, True)
        # print()
        print(f"answer received in {time.time() - start_time_seconds} seconds.")