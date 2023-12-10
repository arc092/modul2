import tkinter as tk
from tkinter import ttk
import sqlite3


class User:
    def __init__(self, username, email, age, gender):
        self.username = username
        self.email = email
        self.age = age
        self.gender = gender


def init_database():
    connection = sqlite3.connect('database.db')
    connection.cursor().execute('''
    CREATE TABLE IF NOT EXISTS 
    Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER,
        gender TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


def upsert_user(user: User) -> str:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM Users WHERE email = ?', (user.email,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute('INSERT INTO Users (username, email, age, gender) VALUES (?, ?, ?, ?)',
                       (user.username, user.email, user.age, user.gender))
        connection.commit()
        connection.close()
        return 'User was created'
    else:
        cursor.execute('UPDATE Users SET username = ?, age = ?, gender = ? WHERE email = ?',
                       (user.username, user.age, user.gender, user.email))
        connection.commit()
        connection.close()
        return 'User was edited'


def get_all_users():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    connection.close()
    return users


def display_users(filter_email=None):
    users = get_all_users()

    users_listbox.delete(0, tk.END)

    for user in users:
        if filter_email is None or filter_email.lower() in user[2].lower():
            users_listbox.insert(
                tk.END, f"{user[1]} ({user[2]}) - Age: {user[3]}, Gender: {user[4]}")


def submit_form():
    username = username_entry.get()
    email = email_entry.get()
    age = age_slider.get()
    gender = gender_var.get()

    if not all([username, email, age, gender]):
        error_label.config(text="Please fill all fields", foreground='red') 
        return

    new_user = User(username, email, round(float(age)), gender)

    result = upsert_user(new_user)
    print(result)
    error_label.config(text=result, foreground='black')

    display_users()

    username_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    gender_var.set(None)
    age_slider.set(1)


def filter_users():
    filter_email = filter_entry.get()
    display_users(filter_email)


def on_user_select(event):
    selected_user = users_listbox.get(users_listbox.curselection())

    selected_email = selected_user.split('(')[1].split(')')[0]

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users WHERE email = ?', (selected_email,))
    selected_user_data = cursor.fetchone()
    connection.close()

    # Fill inputs with the selected user data
    username_entry.delete(0, tk.END)
    username_entry.insert(0, selected_user_data[1])

    email_entry.delete(0, tk.END)
    email_entry.insert(0, selected_user_data[2])

    age_slider.set(selected_user_data[3])
    age_label_value.config(text=f"Selected Age: {selected_user_data[3]}")

    gender_var.set(selected_user_data[4])


root = tk.Tk()
root.title("User Database")

init_database()

username_label = ttk.Label(root, text="Username:")
username_entry = ttk.Entry(root)

email_label = ttk.Label(root, text="Email:")
email_entry = ttk.Entry(root)

age_label = ttk.Label(root, text="Age:")
age_slider = ttk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, length=200,
                       command=lambda value: age_label_value.config(text=f"Selected Age: {round(float(value))}"))
age_label_value = ttk.Label(root, text="Selected Age: 1")

gender_label = ttk.Label(root, text="Gender:")
gender_var = tk.StringVar()
gender_radiobutton_male = ttk.Radiobutton(
    root, text="Male", variable=gender_var, value="Male")
gender_radiobutton_female = ttk.Radiobutton(
    root, text="Female", variable=gender_var, value="Female")

filter_label = ttk.Label(root, text="Filter by Email:")
filter_entry = ttk.Entry(root)
filter_button = ttk.Button(root, text="Filter", command=filter_users)

users_listbox = tk.Listbox(root, height=10, width=50)
users_listbox.bind("<<ListboxSelect>>", on_user_select)

error_label = ttk.Label(root, text="", foreground="red")

submit_button = ttk.Button(root, text="Submit", command=submit_form)

username_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
username_entry.grid(row=0, column=1, padx=5, pady=5)

email_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
email_entry.grid(row=1, column=1, padx=5, pady=5)

age_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
age_slider.grid(row=2, column=1, padx=5, pady=5)
age_label_value.grid(row=2, column=2, padx=5, pady=5)

gender_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
gender_radiobutton_male.grid(row=3, column=1, padx=5, pady=5, sticky="w")
gender_radiobutton_female.grid(row=3, column=2, padx=5, pady=5, sticky="w")

filter_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
filter_entry.grid(row=4, column=1, padx=5, pady=5)
filter_button.grid(row=4, column=2, padx=5, pady=5)

users_listbox.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
error_label.grid(row=6, column=0, columnspan=3, pady=5)

submit_button.grid(row=7, column=0, columnspan=3, pady=10)

display_users()

root.mainloop()
