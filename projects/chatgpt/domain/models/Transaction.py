class Transaction:
    def __init__(self, id: str, date: str, amount: float, description: str, category: str, type: str):
        self.id = id
        self.date = date
        self.amount = amount
        self.description = description
        self.category = category
        self.type = type

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "description": self.description,
            "category": self.category,
            "type": self.type,
        }
