import calendar

from Expense import Expense
from ExpenseManager import ExpenseManager
import datetime
from tabulate import tabulate


def display_menu():
    print("Expense Tracker Menu:")
    print("1. Add Expense")
    print("2. Delete Expense")
    print("3. Update Expense")
    print("4. View All Expenses")
    print("5. View Total Monthly Expenses")
    print("6. Exit")


def get_valid_input(prompt_message):
    while True:
        user_input = input(prompt_message)
        if user_input:
            return user_input
        print("Input cannot be empty. Please try again.")


def get_valid_number(prompt_message):
    while True:
        user_input = input(prompt_message)
        if user_input and user_input.isnumeric():
            return int(user_input)
        print("Please enter a number")


def get_valid_type(prompt_message, valid_types):
    """Validate user input against a list of valid types"""
    while True:
        user_input = input(prompt_message)
        if user_input and user_input in valid_types:
            return user_input
        print("Invalid input. Please enter one of the following: " + ", ".join(valid_types))


def get_valid_date(prompt_message):
    while True:
        date_str = input(prompt_message)
        try:
            # Attempt to parse the input as a date
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date_obj  # Return the datetime object if it's in the correct format
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")


class Coordinator:
    def __init__(self):
        self.expense_manager = ExpenseManager()

    def run(self):
        while True:
            display_menu()
            choice = get_valid_number("Enter your choice: ")

            if choice == 1:
                self.add_expense()
            elif choice == 2:
                self.delete_expense()
            elif choice == 3:
                self.update_expense()
            elif choice == 4:
                self.view_all_expenses()
            elif choice == 5:
                self.view_total_monthly_expenses()
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_expense(self):
        expense_name = get_valid_input("Enter your expense name: ")
        expense_price = get_valid_number("Enter the Cost Price: ")
        expense_amount = get_valid_number("Enter the amount of times the amount was bought: ")
        expense_category = get_valid_type("Choose the categories from these: food, clothing, entertainment, "
                                          "rent, utilities, transportation, other", Expense.valid_categories)
        expense_date = get_valid_date("Enter the date of the expense (YYYY-MM-DD): ")  # Corrected this line
        new_expense = Expense(expense_name, expense_price, expense_amount, expense_category, expense_date)
        self.expense_manager.add_expense_to_database(new_expense)

    def delete_expense(self):
        name = input("Enter expense name to delete: ")
        self.expense_manager.delete_expense_to_database(name)

    def update_expense(self):
        expenses = self.expense_manager.get_all_expenses_from_database()
        if not expenses:
            print("No expenses found.")
            return

        print("Select the expense to update:")
        for idx, expense_obj in enumerate(expenses, 1):
            print(f"{idx}. {expense_obj.name}")

        while True:
            choice = get_valid_input("Enter the number corresponding to the expense: ")
            if choice.isdigit() and 1 <= int(choice) <= len(expenses):
                expense_to_update = expenses[int(choice) - 1]
                break
            print("Invalid choice. Please enter a valid number.")

        # Prompt user for update options
        print("Select what you want to update:")
        print("1. Price")
        print("2. Amount")
        print("3. Category")
        print("4. Date")
        print("5. Update all")
        valid_numbers = ["1", "2", "3", "4", "5"]
        update_choice = get_valid_type("Enter your choice: ", valid_numbers)

        if update_choice == '1':
            new_price = get_valid_number("Enter new expense price: ")
            expense_to_update.price = new_price
        elif update_choice == '2':
            new_amount = get_valid_number("Enter new expense amount: ")
            expense_to_update.amount = new_amount
        elif update_choice == '3':
            new_category = get_valid_type(
                f"Choose the categories from these: {', '.join(Expense.valid_categories)}: ", Expense.valid_categories)
            expense_to_update.category = new_category.lower() if new_category.lower() in Expense.valid_categories else "other"
        elif update_choice == '4':
            new_date = get_valid_date("Enter new expense date (YYYY-MM-DD): ")
            expense_to_update.date = new_date
        elif update_choice == '5':
            new_price = get_valid_number("Enter new expense price: ")
            new_amount = get_valid_number("Enter new expense amount: ")
            new_category = get_valid_type(
                f"Choose the categories from these: {', '.join(Expense.valid_categories)}: ", Expense.valid_categories)
            new_category = new_category.lower() if new_category.lower() in Expense.valid_categories else "other"
            new_date = get_valid_date("Enter new expense date (YYYY-MM-DD): ")
            expense_to_update.price = new_price
            expense_to_update.amount = new_amount
            expense_to_update.category = new_category
            expense_to_update.date = new_date

        try:
            # Update the expense in the database
            self.expense_manager.update_expense_to_database(expense_to_update.name, expense_to_update)
            print("Expense updated successfully.")
        except Exception as e:
            print(f"Error updating expense: {e}")

    def view_all_expenses(self):
        expenses = self.expense_manager.get_all_expenses_from_database()
        if expenses:
            # Prepare data for tabulate
            data = []
            for expense in expenses:
                data.append([expense.name, expense.price, expense.amount, expense.category, expense.date])
            # Print expenses in a tabular format
            print(tabulate(data, headers=["Name", "Price", "Amount", "Category", "Date"], tablefmt="pretty"))
        else:
            print("No expenses found.")

    def view_total_monthly_expenses(self):
        year_month = input("Enter the year and month (YYYY-MM) to view expenses for: ")
        try:
            year, month = map(int, year_month.split('-'))
            self.expense_manager.get_monthly_expenses(month, year)
        except ValueError:
            print("Invalid input format. Please enter the year and month in YYYY-MM format.")

    # def get_monthly_expenses_for_category(self, year, month, category):
    #     # Get the first and last day of the given month
    #     start_date = datetime.datetime(year, month, 1)
    #     # Calculate the last day of the month
    #     last_day_of_month = calendar.monthrange(year, month)[1]
    #     end_date = datetime.datetime(year, month, last_day_of_month)
    #
    #     # Get expenses within the specified month and category
    #     expenses = self.expense_manager.get_expenses_by_date_range(start_date, end_date)
    #     expenses_in_category = [expense for expense in expenses if expense.category.lower() == category.lower()]
    #
    #     # Calculate total expenses for the specified category
    #     total_expenses = sum(expense.price for expense in expenses_in_category)
    #     return total_expenses
    #
    # def get_total_monthly_expense(self, month):
    #     # Get the first and last day of the given month
    #     start_date = datetime.date(month.year, month.month, 1)
    #     last_day_of_month = calendar.monthrange(month.year, month.month)[1]
    #     end_date = datetime.date(month.year, month.month, last_day_of_month)
    #
    #     print("Start Date:", start_date)
    #     print("End Date:", end_date)
    #
    #     # Get expenses within the specified month
    #     expenses = self.expense_manager.get_expenses_by_date_range(start_date, end_date)
    #
    #     print("Expenses Data:", expenses)
    #
    #     # Calculate total expenses for the month
    #     total_expenses = sum(expense.price for expense in expenses)
    #     return total_expenses

    # def view_total_monthly_expenses(self):
    #     year_month = input("Enter the year and month (YYYY-MM) to view expenses for: ")
    #     year_month_split = year_month.split('-')
    #     if len(year_month_split) == 3:
    #         try:
    #             year, month = map(int, year_month_split)
    #             current_month = datetime.date(year, month, 1)
    #             total_monthly_expenses = self.get_total_monthly_expense(current_month)
    #             print(f"Total expenses for {year_month}: {total_monthly_expenses}")
    #         except ValueError:
    #             print("Invalid input format. Please enter the year and month in YYYY-MM format.")
    #     else:
    #         print("Invalid input format. Please enter the year and month in YYYY-MM format.")
    #
    # def view_monthly_expenses_by_category(self):
    #     year_month = input("Enter the year and month (YYYY-MM) to view expenses for: ")
    #     try:
    #         year, month = map(int, year_month.split('-'))
    #         current_month = datetime.datetime(year, month, 1)
    #         category = input("Enter the category to view expenses for: ")
    #         monthly_expenses_for_category = self.get_monthly_expenses_for_category(year, month, category)
    #         print(f"Total expenses for {category} in {year_month}: {monthly_expenses_for_category}")
    #     except ValueError:
    #         print("Invalid input format. Please enter the year and month in YYYY-MM format.")

    def get_total_yearly_expenses(self):
        # Get expenses for the entire year
        expenses = self.expense_manager.get_all_expenses_from_database()

        # Calculate total expenses for the year
        total_expenses = sum(expense.price for expense in expenses)
        return total_expenses

    def get_average_expenses_by_category_for_year(self):
        # Get expenses for the entire year
        expenses = self.expense_manager.get_all_expenses_from_database()

        # Calculate total expenses for each category for the year
        category_expenses = {}
        for expense in expenses:
            category_expenses[expense.category.lower()] = category_expenses.get(expense.category.lower(),
                                                                                0) + expense.price

        # Calculate average expenses for each category for the year
        average_expenses = {category: total_expense / 12 for category, total_expense in category_expenses.items()}
        return average_expenses

    def generate_monthly_expense_report(self, month):
        # Get total monthly expense
        total_monthly_expense = self.get_total_monthly_expense(month)

        # Get average expenses for each category for the year
        average_expenses_by_category = self.get_average_expenses_by_category_for_year()

        # Print total monthly expense
        print(f"Total Monthly Expense: {total_monthly_expense}")

        # Print average expenses for each category for the year
        print("Average Expenses by Category for the Year:")
        for category, average_expense in average_expenses_by_category.items():
            print(f"{category.capitalize()}: {average_expense}")

        # Check if monthly expenses for each category are higher or lower than the average for the year
        print("Comparison of Monthly Expenses with Annual Average:")
        for category, average_expense in average_expenses_by_category.items():
            monthly_expense_for_category = self.get_monthly_expenses_for_category(month, category)
            if monthly_expense_for_category > average_expense:
                print(f"{category.capitalize()}: Monthly expenses higher than average")
            elif monthly_expense_for_category < average_expense:
                print(f"{category.capitalize()}: Monthly expenses lower than average")
            else:
                print(f"{category.capitalize()}: Monthly expenses equal to average")

        # Calculate and print the percentage of expenses for each category out of the total monthly expenses
        print("Percentage of Expenses by Category:")
        for category, average_expense in average_expenses_by_category.items():
            monthly_expense_for_category = self.get_monthly_expenses_for_category(month, category)
            percentage = (monthly_expense_for_category / total_monthly_expense) * 100
            print(f"{category.capitalize()}: {percentage:.2f}%")

