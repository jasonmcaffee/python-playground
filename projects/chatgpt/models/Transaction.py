from datetime import datetime


class Transaction:
    def __init__(self, amount: float, description: str, category: str, date: str, merchant_name: str):
        print('')
        self.amount = amount
        self.description = description
        self.date = date
        self.category = category
        self.merchant_name = merchant_name

    def to_dict(self):
        return {
            "amount": self.amount,
            "description": self.description,
            "date": self.date,
            "category": self.category,
            "merchant_name": self.merchant_name
        }
