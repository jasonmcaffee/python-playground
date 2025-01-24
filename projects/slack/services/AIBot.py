import threading

from slack_sdk.rtm_v2 import RTMClient
from slack_sdk.web import SlackResponse

from projects.slack.config.Config import config
from projects.slack.models.SimpleStreamInferenceCallable import SimpleStreamInferenceCallable, \
    LLMResponseCompletedCallable, LLMTextReceivedCallable
from projects.slack.utils.ai_bot_utils import sanitize_outgoing_slack_message, is_message_addressed_to_ai_bot, \
    parse_summarize_url_command, handle_summarize_url_command, parse_docs_command, handle_docs_command, \
    parse_unknown_command, convert_text_to_slack_blocks


class AIBot:
    """
    AIBot is responsible for listening to slack messages, via RTM, and responding to them using constant message updates
    to emulate streaming responses seen in most chatbot UIs.
    AIBot handles orchestrating calls to the LLM, via the simple_stream_inference function.
    AIBot is called on by main, and expects to be ran in some type of continuous loop.
    e.g. asyncio.ensure_future(ai_bot.start_listening_to_slack_events())
    """

    def __init__(self, simple_stream_inference: SimpleStreamInferenceCallable):
        self.simple_stream_inference = simple_stream_inference
        self.ai_bot_user = config.get_ai_bot_user_slack_handle()
        slack_token = config.get_slack_api_token()
        self.rtm = RTMClient(token=slack_token)

        @self.rtm.on("message")
        def handle(client: RTMClient, event: dict):
            self.handle(client, event)

    def start_listening_to_slack_events(self):
        self.rtm.start()

    def stop_listening_to_slack_events(self):
        self.rtm.close()

    def handle(self, client: RTMClient, event: dict):
        """
        Slack RTM event handler which receives all events for channels, groups, private conversations, etc that AI bot is
        a part of.  If the message is intended for AI bot, then a new thread is spun up, and the message is forwarded to
        handle_ai_bot_message for processing.
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

    def handle_ai_bot_message(self, client: RTMClient, event: dict):
        """
        This function is called when AI bot has been engaged by using "@AI" at the beginning of a slack message.
        It immediately responds to indicate that the message is being processed.
        It then sends the message to an LLM, and streams the response by continuously editing the message as chunks of
        text are streamed back from the LLM.
        This function is expected to run in a thread.
        This function sets up default behaviors for interfacing with a simple streaming LLM, and then forwards those on
        to handle_prompt, which allows for custom behaviors based on the /command used.
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

        # we will get a stream of text chunks from the LLM, which we will append to cumulative text.
        # we will edit the slack message
        cumulative_text = ""
        last_update_length = len(cumulative_text)  # how long cumulative was the last time we performed an update.
        edit_slack_message_after_n_chars_received_from_llm = config.get_edit_slack_message_after_n_chars_received_from_llm()

        # setup default behaviors for how a LLM response is to be handled.
        def handle_response_completed():
            """
            When the LLM has completed its response, we send any remaining cumulative text as the last update.
            :return:
            """
            nonlocal cumulative_text, last_update_length, initial_response
            # Retrieve timestamp of the initial response, which is how we uniquely identify the message, so
            initial_response_ts = initial_response['ts']
            sanitized_cumulative_text = sanitize_outgoing_slack_message(cumulative_text)
            try:
                text_as_blocks = convert_text_to_slack_blocks(sanitized_cumulative_text)
                self.slack_chat_update_message(client=client, channel_id=channel_id,
                                               initial_response_ts=initial_response_ts, blocks=text_as_blocks,
                                               thread_ts=thread_ts)
            except Exception as e:
                print(f'an error has occurred: {e}')
            last_update_length = len(cumulative_text)

        def handle_text_received(text):
            """
            This function is called every time the LLM emits a chunk of text.
            We update the slack response message in batches of 20 chars
            :param text: words or part of a word that has been emitted from the LLM response stream.
            :return:
            """
            # print(f'text from llm received: "{text}" is_response_completed: {is_response_completed}')
            nonlocal cumulative_text, last_update_length, initial_response
            # Retrieve timestamp of the initial response, which is how we uniquely identify the message, so
            initial_response_ts = initial_response['ts']

            if text is not None:
                cumulative_text += text

            # Edit the existing message with the new text
            has_received_enough_text_from_llm = (len(cumulative_text) - last_update_length >=
                                                 edit_slack_message_after_n_chars_received_from_llm)
            # update the original slack message, if appropriate
            # if is_response_completed or has_received_enough_text_from_llm:
            if has_received_enough_text_from_llm:
                try:
                    sanitized_cumulative_text = sanitize_outgoing_slack_message(cumulative_text)
                    text_as_blocks = convert_text_to_slack_blocks(sanitized_cumulative_text)
                    self.slack_chat_update_message(client=client, channel_id=channel_id,
                                                   initial_response_ts=initial_response_ts, blocks=text_as_blocks,
                                                   thread_ts=thread_ts)
                    last_update_length = len(cumulative_text)
                except Exception as e:
                    print(f'an error occurred', e)

        self.handle_prompt(client, event, prompt, handle_text_received, handle_response_completed, initial_response)

    def handle_prompt(self, client: RTMClient, event: dict, prompt: str,
                      default_handle_text_received: LLMTextReceivedCallable,
                      default_handle_response_completed: LLMResponseCompletedCallable, initial_response: SlackResponse):
        """

        :param initial_response: initial response sent to the slack thread, which we update with LLM responses
        :param client: slack client
        :param event: slack event
        :param prompt: message sent to AI bot, minus the @AI at the beginning
        :param default_handle_text_received: default function to be used for streaming LLM responses back to slack
        :param default_handle_response_completed: default function to be used to complete the LLM response back to slack
        :return:
        """
        # parse out potential commands
        potential_summarize_url_command = parse_summarize_url_command(prompt)
        potential_docs_command = parse_docs_command(prompt)
        potential_unknown_command = parse_unknown_command(prompt)

        # check if the command was issued, and forward it on to command handlers, which can customize how the llm is
        # called, prepend & append to the prompt, append to the response message (e.g. with source links), etc.
        if potential_summarize_url_command is not None:
            handle_summarize_url_command(
                potential_summarize_url_command, default_handle_text_received, default_handle_response_completed,
                self.simple_stream_inference)
        elif potential_docs_command is not None:
            handle_docs_command(potential_docs_command, default_handle_text_received,
                                default_handle_response_completed, self.simple_stream_inference)
        elif potential_unknown_command is not None:
            sanitized = sanitize_outgoing_slack_message(potential_unknown_command)
            default_handle_text_received(f"That command is not known: {sanitized}")
            default_handle_response_completed()
        else:
            self.simple_stream_inference(prompt, default_handle_text_received,
                                         default_handle_response_completed)


    def slack_chat_update_message(self, client: RTMClient, channel_id: str, blocks, thread_ts: str,
                                  initial_response_ts: str):
        """
        Slack can intermittently fail, or enforce rate limiting, so we want to retry our interactions.
        :param client:
        :param channel_id:
        :param blocks:
        :param thread_ts:
        :param initial_response_ts:
        :return:
        """
        return client.web_client.chat_update(channel=channel_id,
                                             text='',  # get rid of warning
                                             ts=initial_response_ts,
                                             blocks=blocks,
                                             thread_ts=thread_ts)