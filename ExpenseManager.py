from Expense import Expense
import sqlite3
from datetime import datetime


class ExpenseManager:
    def __init__(self):
        self.conn = sqlite3.connect('expense_tracker.db')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Creates a table in the database"""
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS expense_tracker (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price FLOAT NOT NULL,
        amount INTEGER,
        category TEXT NOT NULL,
        date DATE NOT NULL
        )''')

    def add_expense_to_database(self, expense):
        if isinstance(expense, Expense):
            # Convert date to string representation
            date_str = expense.date.strftime("%Y-%m-%d")
            # Insert expense into the database
            self.c.execute("INSERT INTO expense_tracker (name, price, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                           (expense.name, expense.price, expense.amount, expense.category, date_str))
            self.conn.commit()
            print("Expense added successfully.")
        else:
            print("Invalid expense. Please provide an Expense object.")

    def update_expense_to_database(self, expense_name, new_expense):
        if isinstance(new_expense, Expense):
            # Convert date to string representation
            date_str = new_expense.date.strftime("%Y-%m-%d")
            # Update expense in the database
            self.c.execute("UPDATE expense_tracker SET price=?, amount=?, category=?, date=? WHERE name=?",
                           (new_expense.price, new_expense.amount, new_expense.category,
                            date_str, expense_name))
            if self.c.rowcount == 0:
                print(f"No expense found with the name '{expense_name}'.")
            else:
                print(f"Expense '{expense_name}' updated successfully.")
            self.conn.commit()
        else:
            print("Invalid expense. Please provide an Expense object.")

    def delete_expense_to_database(self, expense_name):
        self.c.execute("DELETE FROM expense_tracker WHERE name=?", (expense_name,))
        if self.c.rowcount == 0:
            print(f"No expense found with the name '{expense_name}'.")
        else:
            print(f"Expense '{expense_name}' deleted successfully.")
        self.conn.commit()  # This is line 40

    def get_total_expenses(self):
        self.c.execute("SELECT SUM(price) FROM expense_tracker")
        total_expenses = self.c.fetchone()[0]
        return total_expenses if total_expenses else 0

    def get_expenses_by_category(self, category):
        category = category.lower()
        self.c.execute("SELECT * FROM expense_tracker WHERE category=?", (category,))
        return self.c.fetchall()

    def get_expenses_by_date_range(self, start_date, end_date):
        self.c.execute("SELECT * FROM expense_tracker WHERE date BETWEEN ? AND ?", (start_date, end_date))
        expenses_data = self.c.fetchall()
        expenses = []
        for row in expenses_data:
            expense = Expense(row[1], row[2], row[3], row[4], row[5])
            expenses.append(expense)
        return expenses

    def get_all_expenses_from_database(self):
        self.c.execute("SELECT * FROM expense_tracker")
        expenses = []
        for row in self.c.fetchall():
            # Convert date string to datetime.date object
            date_obj = datetime.strptime(row[5], "%Y-%m-%d").date()
            expense = Expense(row[1], row[2], row[3], row[4], date_obj)
            expenses.append(expense)
        return expenses

    def get_monthly_expenses(self, month, year):
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

        # Total monthly expenses
        self.c.execute("SELECT SUM(amount) FROM expense_tracker WHERE date >= ? AND date < ?", (start_date, end_date))
        total_monthly_expense = self.c.fetchone()[0]

        # Total annual expenses
        start_year = datetime(year, 1, 1).strftime('%Y-%m-%d')
        end_year = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
        self.c.execute("SELECT category, SUM(amount) FROM expense_tracker WHERE date >= ? AND date < ? GROUP BY category",
                       (start_year, end_year))
        annual_expenses_by_category = self.c.fetchall()

        # Average expenses for each category for the year
        average_expenses_by_category = {category: total / 12 for category, total in annual_expenses_by_category}

        # Total expenses for the month by category
        self.c.execute("SELECT category, SUM(amount) FROM expense_tracker WHERE date >= ? AND date < ? GROUP BY category",
                       (start_date, end_date))
        monthly_expenses_by_category = self.c.fetchall()

        # Display monthly expense report
        print(f"Monthly Expense Report for {datetime(year, month, 1).strftime('%B %Y')}:")
        print("Category      |   Total Expense   |   Percentage   |   Annual Avg   |   Comparison")

        # Calculate maximum column widths
        max_category_width = max(len(category) for category, _ in monthly_expenses_by_category) + 3
        max_total_width = max(len(f"${total:.2f}") for _, total in monthly_expenses_by_category) + 3
        max_percentage_width = max(
            len(f"{(total / total_monthly_expense) * 100:.2f}%") for _, total in monthly_expenses_by_category) + 3
        max_annual_avg_width = max(len(f"${average_expenses_by_category.get(category, 0):.2f}") for category, _ in
                                   monthly_expenses_by_category) + 3

        # Print table header
        print(
            "-" * (max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(" | ") * 4))

        # Print table rows
        for category, total in monthly_expenses_by_category:
            category_percentage = (total / total_monthly_expense) * 100
            annual_avg = average_expenses_by_category.get(category, 0)
            comparison = "Higher" if total > annual_avg else "Lower" if total < annual_avg else "Equal"

            print(
                f"{category:<{max_category_width}} |   ${total:>{max_total_width - 1}.2f}   |   {category_percentage:>{max_percentage_width - 1}.2f}%  |   ${annual_avg:>{max_annual_avg_width - 1}.2f}  |   {comparison}")

        # Print bottom line of table
        print(
            "-" * (max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(" | ") * 4))

    def get_expense_by_id(self, expense_id):
        self.c.execute("SELECT * FROM expense_tracker WHERE id=?", (expense_id,))
        expense = self.c.fetchone()
        if expense:
            return expense
        else:
            print(f"No expense found with ID '{expense_id}'.")
            return None

    def __del__(self):
        """Closes the database"""
        self.conn.close()
