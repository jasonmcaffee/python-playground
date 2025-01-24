import re
import textwrap

import requests
from bs4 import BeautifulSoup

from projects.slack.models.SimpleStreamInferenceCallable import LLMResponseCompletedCallable, LLMTextReceivedCallable, \
    SimpleStreamInferenceCallable


def escape_slack_user_mentions(text: str):
    """
    Escape mentions of users in a Slack message so they do not trigger user mentions.
    :param text: str, the original Slack message
    :return: str, the escaped message
    """
    # Replace Slack user mention patterns (like <@UEU96U15F>) with the user ID in backticks
    escaped_message = re.sub(r'<@(U[A-Z0-9]+)>', r'`\1`', text)
    return escaped_message


def sanitize_outgoing_slack_message(text: str):
    """
    Prevent our bot from performing slack related operations, such as mentioning other users.
    todo: also prevent all slack operations, like slash commands, etc.
    :param text: str,  message to sanitize
    :return: str, sanitized message
    """
    text_without_user_mentions = escape_slack_user_mentions(text)
    return text_without_user_mentions


def is_message_addressed_to_ai_bot(message: str, ai_bot_user: str):
    """
    determines whether the slack message is addressed to AI bot
    :param ai_bot_user: username of the ai bot e.g. "<@U39529S5>"
    :param message: message text from the slack event
    :return:
    """
    return message.startswith(ai_bot_user)


def parse_docs_command(message: str):
    if not message.startswith('/docs '):
        return

        # Regular expression to match the command pattern with a more inclusive URL pattern
    pattern = r'^(\/docs)\s+(.*)$'
    match = re.match(pattern, message)

    if match:
        print(f'docs match: {match}')
        slash_command, new_message_with_command_stripped = match.groups()
        return new_message_with_command_stripped, slash_command
    else:
        raise ValueError(f"Invalid message format: {message}")


def parse_unknown_command(message: str):
    if not message.startswith('/'):
        return
    return message


def handle_docs_command(potential_command: object, default_handle_text_received: LLMTextReceivedCallable,
                        default_handle_response_completed: LLMResponseCompletedCallable,
                        simple_stream_inference: SimpleStreamInferenceCallable):
    new_message_with_command_stripped, slash_command = potential_command
    custom_message = textwrap.dedent(f"""
        The /docs command is currently not supported, but if it were, the response would look like:
        {sanitize_outgoing_slack_message(new_message_with_command_stripped)}
        The answer to your question is: blah blah
        In order to answer your question, I analyzed the following sources
    """)
    # still send something to the LLM to ensure things are wired up appropriately.
    new_prompt = "Repeat this exact phrase without any additional text: '\n'"

    def handle_text_received(text: str):
        default_handle_text_received(text)

    def handle_response_completed():
        sources = """\nSources: \n<https://orcas.com>\n<https://whales.com>"""
        default_handle_text_received(sources)
        default_handle_response_completed()

    default_handle_text_received(custom_message)
    simple_stream_inference(new_prompt, handle_text_received, handle_response_completed)


def parse_summarize_url_command(message: str):
    """
    Parse a message that starts with a command '/summarize-url' followed by a well-formatted URL.

    :param message: str, the message to parse
    :return: tuple, (new_message_with_command_stripped, slash_command, url)
    :raises ValueError: if the URL is invalid
    """
    if not message.startswith('/summarize-url '):
        return

        # Regular expression to match the command pattern with a more inclusive URL pattern
    pattern = r'^(\/summarize-url)\s+<([^>]+)>(.*)$'
    match = re.match(pattern, message)

    if match:
        slash_command, url, new_message_with_command_stripped = match.groups()
        return new_message_with_command_stripped, slash_command, url
    else:
        raise ValueError(f"Invalid message format or URL: {message}")


def handle_summarize_url_command(potential_command: object, default_handle_text_received: LLMTextReceivedCallable,
                                 default_handle_response_completed: LLMResponseCompletedCallable,
                                 simple_stream_inference: SimpleStreamInferenceCallable):
    new_message_with_command_stripped, slash_command, url = potential_command
    html_content = get_html_content(url)
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
    simple_stream_inference(new_prompt, default_handle_text_received, default_handle_response_completed)


def get_html_content(url: str):
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


def convert_text_to_slack_blocks(text: str):
    """
    We must use rich_text as our reply type.  mrkdown sections get collapsed with "show more" for each one.
    Rich text allows us to send up to 13k characters.  "mrkdown" only allows for 3k
    The downside is that rich text doesn't display markdown :/

    Converts a long text into a list of Slack message blocks, each containing up to 3000 characters of the text.

    :param text: The text to be converted into Slack blocks.
    :return: A list of Slack blocks, each containing a chunk of the text.
    """
    # Calculate the number of chunks needed for the given text
    chunk_size = 13000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Create a block for each chunk
    blocks = []
    for text_chunk in chunks:
        # block = {
        #     "type": "section",
        #     "text": {
        #         "type": "mrkdwn",
        #         "text": text_chunk  # Each chunk must be less than 3001 chars
        #     }
        # }
        block = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": text_chunk
                        },
                    ]
                }
            ]
        }
        blocks.append(block)

    return blocks
