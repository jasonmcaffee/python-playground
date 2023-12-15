from typing import List

from projects.chatgpt.domain.models.Transaction import Transaction


class Account:
    def __init__(self, id: str, transactions: List[Transaction], account_type: str, account_name: str):
        self.id = id
        self.transactions = transactions
        self.account_type = account_type
        self.account_name = account_name

    def to_dict(self):
        return {
            "id": self.id,
            "transactions": self.transactions,
            "account_type": self.account_type,
        }
