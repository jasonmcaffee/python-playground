import json
import textwrap
import psycopg2
import csv
import io

from projects.chatgpt.decorators.chatgpt_tool_data import chatgpt_tool_data
from projects.chatgpt.services.llm_callable_functions.CallableFunctionServiceBase import CallableFunctionServiceBase

conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgrespw',
    'host': 'localhost',
    'port': '55000',
    'options': '-c search_path=financial_data',
}

class TransactionQueries(CallableFunctionServiceBase):
    def __init__(self):
        super().__init__()
        self.connection = psycopg2.connect(**conn_params)

    @chatgpt_tool_data({
        "type": "function",
        "function": {
            "name": "transaction_query",
            "description": textwrap.dedent("""Function to answer questions related to a persons financial spending habits, accounts, balances, and transactions.
            Uses the passed in postgres sql query to retrieve financial transaction data, such as transactions between a certain date, accounts, transactions for a certain category, etc.
            When a category is searched for, text case should be ignored, and the bot should understand that some transactions will have variances on the same category. e.g. 'Food' might also be 'Dining', so the bot should find perform semantic searches for categories with similar meaning.
            When an account type is searched for, text case should be ignored, and the bot should perform semantic search. .e.g. 'Credit' is the same as 'credit card'
            Return value will be the result of the sql query as a csv string, or an exception message from psycopg2.  
            If the bot receives an exception, it should try another sql query for a maximum of 5 times.
            """)
            ,
            "parameters": {
                "type": "object",
                "properties": {
                    "postgres_sql_query": {
                        "type": "string",
                        "description": textwrap.dedent(
                            """The generated postgres sql query, created by the bot, which queries the tables described below.
                            All queries should ignore text case when matching category and account_type.
                            The bot should use join statements when necessary.
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
        # print(f"transactions_query called with args {arguments}")
        postgres_sql_query = arguments['postgres_sql_query']
        csv_results = self.query_to_csv_string(self.connection, postgres_sql_query)
        print(f"transaction_query called with query: \n{postgres_sql_query}")
        print(f"query result:\n {csv_results}")
        return csv_results

    def query_to_csv_string(self, connection, query):
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            # Column names from the cursor
            col_names = [desc[0] for desc in cursor.description]
            output = io.StringIO()   # Create a CSV output from the results
            csv_writer = csv.writer(output)
            csv_writer.writerow(col_names)  # Write the header
            csv_writer.writerows(results)  # Write the data
            # Get the CSV string
            csv_string = output.getvalue()
            output.close()
            return csv_string
        except Exception as e:
            return str(e)
        finally:
            if 'cursor' in locals():
                cursor.close()
