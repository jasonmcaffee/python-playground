import json
from datetime import datetime

from projects.chatgpt.decorators.chatgpt_tool_data import chatgpt_tool_data
from projects.chatgpt.models.Transaction import Transaction
from projects.chatgpt.services.llm_callable_functions.CallableFunctionServiceBase import CallableFunctionServiceBase


# Demo service which provides ChatGPT the ability to call method get_user_details, which supplies a hard-coded result.
class UserDetails(CallableFunctionServiceBase):
    def __init__(self):
        super().__init__()

    @chatgpt_tool_data({
        "type": "function",
        "function": {
            "name": "find_financial_transactions",
            "description": "Retrieves financial transaction data which has been filtered based on the search criteria passed as arguments."
                "Return value will be an array of transactions in JSON format."
                "e.g. ["
                    "{ 'merchant_name': 'Walmart', 'amount': 24.56, 'date':'2023-03-15T10:12:45.12', 'category': 'groceries', 'description': 'Food' }"           
                "]",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date_iso": {
                        "type": "string",
                        "description": "ISO 8601 formatted date string.  If provided, this function will only return transactions that occurred after the start date."
                    },
                    "end_date_iso": {
                        "type": "string",
                        "description": "ISO 8601 formatted date string.  If provided, this function will only return transactions that occurred before the end date."
                    }
                },
                "required": []
            }
        }
    })
    def find_financial_transactions(self, args: str):
        arguments = json.loads(args)
        print(f"get_transactions_for_date_range function called with arguments {arguments}")
        transaction1 = Transaction(amount=123.05, description='', category='Groceries', date='2023-03-15T10:12:45.12', merchant_name='Walmart')
        transaction2 = Transaction(amount=53.12, description='', category='Gas', date='2023-03-14T11:34:33.16', merchant_name='Chevron')
        transaction3 = Transaction(amount=433.00, description='', category='Shopping', date='2023-03-13T11:22:45.07', merchant_name='Amazon')
        response = [
            transaction1.to_dict(),
            transaction2.to_dict(),
            transaction3.to_dict()
        ]
        text_response = json.dumps(response)
        return text_response


    @chatgpt_tool_data({
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "Retrieves information for a user based on the combination of their first and last names.  "
                           "It returns information about the user's age, location, and profession.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "First name of the user to get details of."
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Last name of the user to get details of."
                    }
                },
                "required": ["first_name", "last_name"]
            }
        },
    })
    def get_user_details(self, args):
        arguments = json.loads(args)
        print(
            f"get_user_details function called with arguments first_name: {arguments['first_name']}, last_name: {arguments['last_name']}")
        response = {
            "age": 44,
            "location": {
                "state": "Utah"
            },
            "profession": "Software Engineer"
        }
        text_response = json.dumps(response)
        print(f"get_user_details is returning: {text_response}")
        return text_response
