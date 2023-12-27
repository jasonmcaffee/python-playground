import threading
import os
import re
import requests
from dotenv import load_dotenv
from slack_sdk.rtm_v2 import RTMClient
from projects.slack.services.SimpleChatGPT import SimpleChatGPT
from bs4 import BeautifulSoup

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
        # print(event)
        if self.is_message_addressed_to_ai_bot(message_received):
            # start a new thread to handle the message
            thread = threading.Thread(target=self.handle_ai_bot_message, args=(client, event))
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
        prompt = prompt.lstrip()  # strip any leading whitespace

        # Initial message sent to the channel
        initial_response = client.web_client.chat_postMessage(channel=channel_id, text="...", thread_ts=thread_ts)
        # Retrieve timestamp of the initial response, which is how we uniquely identify the message, so
        initial_response_ts = initial_response['ts']

        # check to see if there are any commands in the message, and modify the prompt.  e.g. summarize-url will fetch
        # the url then send it to the LLM
        try:
            prompt = self.modify_prompt_based_on_command(prompt)
        except Exception as e:
            message = f"There was an issue with your request: {e}"
            client.web_client.chat_update(channel=channel_id, ts=initial_response_ts, text=message, thread_ts=thread_ts)
            return

        # we will get a stream of text chunks from the LLM, which we will append to cumulative text.
        # we will edit the slack message
        cumulative_text = ""
        last_update_length = len(cumulative_text)  # how long cumulative was the last time we performed an update.
        edit_slack_message_after_n_chars_received_from_llm = 20

        def handle_response_completed():
            nonlocal cumulative_text, last_update_length
            sanitized_cumulative_text = self.sanitize_output(cumulative_text)
            client.web_client.chat_update(channel=channel_id, ts=initial_response_ts, text=sanitized_cumulative_text,
                                          thread_ts=thread_ts)
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
                client.web_client.chat_update(channel=channel_id, ts=initial_response_ts,
                                              text=sanitized_cumulative_text, thread_ts=thread_ts)
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

    def modify_prompt_based_on_command(self, prompt):
        """
        certain prompt contains commands
        :param prompt:
        :return:
        """

        potential_summarize_url_command = self.parse_summarize_url_command(prompt)
        if potential_summarize_url_command is not None:
            prompt = self.modify_prompt_to_summarize_url(potential_summarize_url_command)

        return prompt

    def modify_prompt_to_summarize_url(self, potential_summarize_url_command):
        new_message_with_command_stripped, slash_command, url = potential_summarize_url_command
        html_content = self.get_html_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract text
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'}) or soup.find(
            'div', class_=lambda x: x and 'content' in x)

        # Extract text from the main content if found
        if main_content:
            website_as_text = main_content.get_text(separator='\n', strip=True)
        else:
            website_as_text = soup.get_text(separator='\n', strip=True)
            print("Main content not found.")

        partial_website_as_text = website_as_text[0:2000]  # avoid going over our token limit.

        new_prompt = f"This text is from a website where the html was parsed using BeautifulSoup. Please summarize this text into 300 words or less: \n {partial_website_as_text}"
        return new_prompt

    def parse_summarize_url_command(self, message):
        """
        Parse a message that starts with a command '/summarize-url' followed by a well-formatted URL.

        :param message: str, the message to parse
        :return: tuple, (new_message_with_command_stripped, slash_command, url)
        :raises ValueError: if the URL is invalid
        """
        if not message.startswith('/summarize-url'):
            return

            # Regular expression to match the command pattern with a more inclusive URL pattern
        pattern = r'^(\/summarize-url)\s+<([^>]+)>(.*)$'
        match = re.match(pattern, message)

        if match:
            slash_command, url, new_message_with_command_stripped = match.groups()
            return new_message_with_command_stripped, slash_command, url
        else:
            raise ValueError(f"Invalid message format or URL: {message}")

    def get_html_content(self, url: str):
        """
            Retrieve the raw HTML content of a URL.

            :param url: str, the URL to retrieve
            :return: str, the raw HTML content
            :raises Exception: if the response status code is not 2xx
            """
        response = requests.get(url)

        # Check if the response status code is in the 2xx success range
        if response.status_code // 100 == 2:
            return response.text
        else:
            raise Exception(f"Failed to retrieve URL. Status code: {response.status_code}")
