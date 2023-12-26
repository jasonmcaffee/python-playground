
import threading

from slack_sdk.rtm_v2 import RTMClient

# Load your Slack API token
with open('projects/slack/slack-api-token.txt', 'r') as file:
    slack_token = file.read().strip()

# Initialize the RTMClient
rtm = RTMClient(token=slack_token)
# rtm.start()

class AIBot:

    def __init__(self):
        self.ai_bot_user = "<@U06ANF43Q57>"
        @rtm.on("message")
        def handle(client: RTMClient, event: dict):
            self.handle(client, event)


    def kill(self):
        rtm.close()

    def start(self):
        rtm.start()

    # Define the event handler
    def handle(self, client: RTMClient, event: dict):
        message_received = event.get('text', '')
        # user = event['user']  # User ID


        # Post a message to the channel
        # Check if the message is addressed to @ai
        # if message_received.startswith(ai_bot_user):
        if self.is_message_addressed_to_ai_bot(message_received):
            print('ai_bot_user')

            def handle_ai_bot_message(client: RTMClient, event: dict):
                # print(f'handle ai bot message: {event}')
                message_received = event.get('text', '')
                channel_id = event['channel']
                thread_ts = event['ts']

                prompt = message_received.replace(self.ai_bot_user, '')
                cumulative_text = f"..."
                # print(cumulative_text)
                # Initial message sent to the channel
                initial_response = client.web_client.chat_postMessage(
                    channel=channel_id,
                    text=cumulative_text,
                    thread_ts=thread_ts
                )
                cumulative_text = ""

                # Retrieve timestamp of the initial response
                initial_response_ts = initial_response['ts']
                last_update_length = len(cumulative_text)

                def handle_text_received(text, is_response_completed):
                    # print(f'text from llm received: {text} \nis_response_completed: {is_response_completed}')
                    nonlocal cumulative_text, last_update_length
                    cumulative_text += text
                    # print(text, end='')
                    # Edit the existing message with the new text
                    if len(cumulative_text) - last_update_length >= 20 or is_response_completed:
                        client.web_client.chat_update(
                            channel=channel_id,
                            ts=initial_response_ts,  # Timestamp of the message to update
                            text=cumulative_text,
                            thread_ts=thread_ts
                        )
                        last_update_length = len(cumulative_text)

                self.llm_prompt(prompt, handle_text_received)

            thread = threading.Thread(
                target=handle_ai_bot_message,
                args=(client, event)
            )
            thread.start()
            # handle_ai_bot_message(client, event)


    def llm_prompt(self, prompt, handle_text_received):
        handle_text_received(f'hello', is_response_completed=True)


    def is_message_addressed_to_ai_bot(self, message):
        return message.startswith(self.ai_bot_user)

