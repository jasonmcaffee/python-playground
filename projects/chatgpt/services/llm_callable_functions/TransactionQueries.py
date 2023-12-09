import json
import textwrap

from projects.chatgpt.decorators.chatgpt_tool_data import chatgpt_tool_data
from projects.chatgpt.services.llm_callable_functions.CallableFunctionServiceBase import CallableFunctionServiceBase


class TransactionQueries(CallableFunctionServiceBase):
    def __init__(self):
        super().__init__()

    @chatgpt_tool_data({
        "type": "function",
        "function": {
            "name": "transaction_query",
            "description": textwrap.dedent("""Function to answer questions related to a persons financial spending habits, accounts, balances, and transactions.
            Uses the passed in postgres sql query to retrieve financial transaction data, such as transactions between a certain date, accounts, transactions for a certain category, etc.
            Return value will be the result of the sql query as a csv string.
            """)
            ,
            "parameters": {
                "type": "object",
                "properties": {
                    "postgres_sql_query": {
                        "type": "string",
                        "description": textwrap.dedent(
                            """The generated postgres sql query, created by the bot, which queries the tables described in the description of this function.
                            The tables available are: 
                            CREATE TABLE  if not exists Account ( # Table for storing account details
                                id VARCHAR(255) PRIMARY KEY,
                                account_type VARCHAR(255), # Type of the account e.g. savings, checking, credit card, investment, mortgage, personal loan, etc
                                account_name VARCHAR(255) # Name of the account e.g. Primary Checking, Student Loan, Chase Saphire Credit Card
                            );
                            CREATE TABLE if not exists Transaction ( # Table for storing transaction details for accounts
                                id VARCHAR(255) PRIMARY KEY,
                                date DATE, # Date when the transaction occurred. e.g. "12/5/22"
                                amount FLOAT,
                                description TEXT, # Description of the transaction which includes the other parties involved in the transaction.  e.g. "DELTA AIR   0062355335690", "TRADER JOE''S #350 QPS", "UBER   TRIP"
                                type varchar(255), # The credit or debit type. e.g. "Sale", "Payment"
                                category VARCHAR(255), # Category of the transaction (e.g., groceries, utilities, Loan payment, ACH Credit, Other, Food & Drink, Gifts & Donations)
                                account_id VARCHAR(255) REFERENCES Account(id)
                            );
                        """)
                    },
                },
                "required": ["postgres_sql_query"]
            }
        }
    })
    def transaction_query(self, args: str):
        arguments = json.loads(args)
        print(f"transactions_query called with args {arguments}")
        postgres_sql_query = arguments['postgres_sql_query']
