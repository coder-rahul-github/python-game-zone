import tkinter as tk
from tkinter import messagebox

# Initialize the data structure from the source (list of dictionaries)
expenses_list = []

def add_expense():
    # Retrieve data from input fields
    date = entry_date.get()
    category = entry_category.get()
    description = entry_description.get()
    try:
        amount = float(entry_amount.get())
        
        # Create dictionary as per source logic
        expense = {
            "date": date,
            "category": category,
            "description": description,
            "amount": amount
        }
        expenses_list.append(expense)
        messagebox.showinfo("Success", "Done bro! Expenses added successfully.")
        
        # Clear fields after adding
        entry_date.delete(0, tk.END)
        entry_category.delete(0, tk.END)
        entry_description.delete(0, tk.END)
        entry_amount.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for amount.")

def view_all():
    if not expenses_list:
        messagebox.showinfo("Info", "No expenses added yet.")
        return
    
    display_text = "--- Your Expenses ---\n"
    for i, exp in enumerate(expenses_list, 1):
        display_text += f"{i}. {exp['date']} | {exp['category']} | {exp['amount']}\n"
    
    messagebox.showinfo("All Expenses", display_text)

def show_total():
    # Calculation logic from the source
    total = sum(exp['amount'] for exp in expenses_list)
    messagebox.showinfo("Total Spending", f"Total Spending: {total}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("300x400")

# Labels and Entry fields for the 4 required pieces of information
tk.Label(root, text="Date (DD-MM-YYYY):").pack()
entry_date = tk.Entry(root)
entry_date.pack()

tk.Label(root, text="Category (Food/Travel/etc):").pack()
entry_category = tk.Entry(root)
entry_category.pack()

tk.Label(root, text="Description:").pack()
entry_description = tk.Entry(root)
entry_description.pack()

tk.Label(root, text="Amount:").pack()
entry_amount = tk.Entry(root)
entry_amount.pack()

tk.Button(root, text="Add Expense", command=add_expense, bg="green", fg="white").pack(pady=10)
tk.Button(root, text="View All Expenses", command=view_all).pack(pady=5)
tk.Button(root, text="View Total Spending", command=show_total).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit).pack(pady=20)

root.mainloop()