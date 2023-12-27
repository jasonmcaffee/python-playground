import threading
import os
import re
from dotenv import load_dotenv
from slack_sdk.rtm_v2 import RTMClient
from projects.slack.services.SimpleChatGPT import SimpleChatGPT

load_dotenv()
slack_token = os.getenv('SLACK_API_TOKEN')

# Initialize the RTMClient
rtm = RTMClient(token=slack_token)


# rtm.start()

class AIBot:

    def __init__(self):
        self.ai_bot_user = "<@U06ANF43Q57>"
        self.llm = SimpleChatGPT()

        @rtm.on("message")
        def handle(client: RTMClient, event: dict):
            self.handle(client, event)

    def kill(self):
        """
        Main function should call this to have AI bot stop listening to slack events.
        :return:
        """
        rtm.close()

    def start(self):
        """
        Main function should call this to have AI bot start listening to slack events.
        :return:
        """
        rtm.start()

    # Define the event handler
    def handle(self, client: RTMClient, event: dict):
        """
        Slack RTM event handler which receives all events for channels, groups, private conversations, etc that AI bot is
        a part of.
        :param client:
        :param event:
        :return:
        """
        message_received = event.get('text', '')
        if self.is_message_addressed_to_ai_bot(message_received):
            print('ai_bot_user')

            thread = threading.Thread(
                target=self.handle_ai_bot_message,
                args=(client, event)
            )
            thread.start()
            # handle_ai_bot_message(client, event)

    def handle_ai_bot_message(self, client: RTMClient, event: dict):
        """
        This function is called when AI bot has been engaged by using "@AI" at the beginning of a slack message.
        It immediately responds to indicate that the message is being processed.
        It then sends the message to an LLM, and streams the response by continuously editing the message as chunks of
        text are streamed back from the LLM.
        This function is expected to run in a thread.
        :param client: slack client
        :param event: slack event, including time, message, who sent the message, etc.
        :return:
        """
        # print(f'handle ai bot message: {event}')
        message_received = event.get('text', '')
        channel_id = event['channel']
        thread_ts = event['ts']

        # parse the prompt the user has sent AI by removing the @AI from the prompt.
        prompt = message_received.replace(self.ai_bot_user, '')

        # Initial message sent to the channel
        initial_response = client.web_client.chat_postMessage(channel=channel_id, text="...", thread_ts=thread_ts)

        # Retrieve timestamp of the initial response, which is how we uniquely identify the message, so
        initial_response_ts = initial_response['ts']

        # we will get a stream of text chunks from the LLM, which we will append to cumulative text.
        # we will edit the slack message
        cumulative_text = ""
        last_update_length = len(cumulative_text) # how long cumulative was the last time we performed an update.
        edit_slack_message_after_n_chars_received_from_llm = 20

        def handle_response_completed():
            nonlocal cumulative_text, last_update_length
            sanitized_cumulative_text = self.sanitize_output(cumulative_text)
            client.web_client.chat_update(channel=channel_id, ts=initial_response_ts, text=sanitized_cumulative_text, thread_ts=thread_ts)
            last_update_length = len(cumulative_text)

        def handle_text_received(text):
            # print(f'text from llm received: "{text}" is_response_completed: {is_response_completed}')
            nonlocal cumulative_text, last_update_length

            if text is not None:
                cumulative_text += text

            # Edit the existing message with the new text
            has_received_enough_text_from_llm = (len(cumulative_text) - last_update_length >=
                                                 edit_slack_message_after_n_chars_received_from_llm)
            # update the original slack message, if appropriate
            # if is_response_completed or has_received_enough_text_from_llm:
            if has_received_enough_text_from_llm:
                sanitized_cumulative_text = self.sanitize_output(cumulative_text)
                client.web_client.chat_update(channel=channel_id, ts=initial_response_ts, text=sanitized_cumulative_text, thread_ts=thread_ts)
                last_update_length = len(cumulative_text)

        self.llm_prompt(prompt, handle_text_received, handle_response_completed)

    def llm_prompt(self, prompt, handle_text_received, handle_response_complete):
        # handle_text_received(f'hello', is_response_completed=True)
        self.llm.stream_prompt(prompt, handle_text_received, handle_response_complete)

    def is_message_addressed_to_ai_bot(self, message):
        return message.startswith(self.ai_bot_user)

    def sanitize_output(self, text):
        text_without_user_mentions = self.escape_slack_user_mentions(text)
        return text_without_user_mentions

    def escape_slack_user_mentions(self, text):
        """
        Escape mentions of users in a Slack message so they do not trigger user mentions.

        :param text: str, the original Slack message
        :return: str, the escaped message
        """
        # Replace Slack user mention patterns (like <@UEU96U15F>) with the user ID in backticks
        escaped_message = re.sub(r'<@(U[A-Z0-9]+)>', r'`\1`', text)
        return escaped_message
