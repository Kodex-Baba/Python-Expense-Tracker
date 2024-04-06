import datetime


class Expense:
    valid_categories = ["food", "clothing", "entertainment", "rent", "utilities", "transportation", "other"]

    def __init__(self, name, price, amount, category, date):
        self.name = name
        self.price = price
        self.amount = amount
        self.category = category.lower() if category.lower() in self.valid_categories else "other"
        if isinstance(date, datetime.date):
            self.date = date
        else:
            raise ValueError("Date should be a datetime.date object")

    def __str__(self):
        return f"Name: {self.name}, Price: {self.price}, Amount: {self.amount}, Category: {self.category}, Date: {self.date}"
