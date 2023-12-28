import threading

from slack_sdk.rtm_v2 import RTMClient

from projects.slack.config.Config import config
from projects.slack.models.SimpleStreamInferenceCallable import SimpleStreamInferenceCallable
from projects.slack.utils.ai_bot_utils import sanitize_outgoing_slack_message, is_message_addressed_to_ai_bot, \
    parse_summarize_url_command, modify_prompt_for_summarize_url, parse_docs_command, modify_prompt_for_docs_command


class AIBot:

    def __init__(self, simple_stream_inference_callable: SimpleStreamInferenceCallable,
                 ai_bot_user: str = "<@U06ANF43Q57>"):
        self.simple_stream_inference_callable = simple_stream_inference_callable
        self.ai_bot_user = ai_bot_user
        slack_token = config.get_slack_api_token()
        # Initialize the RTMClient
        self.rtm = RTMClient(token=slack_token)

        @self.rtm.on("message")
        def handle(client: RTMClient, event: dict):
            self.handle(client, event)

    def stop_listening_to_slack_events(self):
        """
        Main function should call this to have AI bot stop listening to slack events.
        :return:
        """
        self.rtm.close()

    def start_listening_to_slack_events(self):
        """
        Main function should call this to have AI bot start listening to slack events.
        :return:
        """
        self.rtm.start()

    # Define the event handler
    def handle(self, client: RTMClient, event: dict):
        """
        Slack RTM event handler which receives all events for channels, groups, private conversations, etc that AI bot is
        a part of.
        :param client: slack client
        :param event: slack event
        :return:
        """
        message_received = event.get('text', '')
        # print(event)
        if is_message_addressed_to_ai_bot(message_received, self.ai_bot_user):
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
            """
            When the LLM has completed its response, we send any remaining cumulative text as the last update.
            :return:
            """
            nonlocal cumulative_text, last_update_length
            sanitized_cumulative_text = sanitize_outgoing_slack_message(cumulative_text)
            client.web_client.chat_update(channel=channel_id, ts=initial_response_ts, text=sanitized_cumulative_text,
                                          thread_ts=thread_ts)
            last_update_length = len(cumulative_text)

        def handle_text_received(text):
            """
            This function is called every time the LLM emits a chunk of text.
            We update the slack response message in batches of 20 chars
            :param text: words or part of a word that has been emitted from the LLM response stream.
            :return:
            """
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
                sanitized_cumulative_text = sanitize_outgoing_slack_message(cumulative_text)
                client.web_client.chat_update(channel=channel_id, ts=initial_response_ts,
                                              text=sanitized_cumulative_text, thread_ts=thread_ts)
                last_update_length = len(cumulative_text)

        self.simple_stream_inference_callable(prompt, handle_text_received, handle_response_completed)

    def modify_prompt_based_on_command(self, prompt):
        """
        First attempt at allowing for commands. e.g. @AI /summarize-url https://google.com
        I think this needs to be refactored, as some custom functions might
        want to control sending the message to slack themselves...
        :param prompt: str, the prompt to be sent to the llm
        :return:
        """
        potential_summarize_url_command = parse_summarize_url_command(prompt)
        if potential_summarize_url_command is not None:
            prompt = modify_prompt_for_summarize_url(potential_summarize_url_command)

        potential_docs_command = parse_docs_command(prompt)
        if potential_docs_command is not None:
            prompt = modify_prompt_for_docs_command(potential_docs_command)

        return prompt
