import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = 'password_manager.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "passwords": {}}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.data = load_data()
        self.logged_in_user = None
        self.login_screen()

    def login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Login", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.root, text="Username").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack()
        tk.Label(self.root, text="Password").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()

        def login():
            username = username_entry.get()
            password = password_entry.get()
            if username in self.data['users'] and self.data['users'][username] == password:
                self.logged_in_user = username
                self.dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password")

        tk.Button(self.root, text="Login", command=login, width=20).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register_screen, width=20).pack(pady=5)

    def register_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Register", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.root, text="Username").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack()
        tk.Label(self.root, text="Password").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()

        def register():
            username = username_entry.get()
            password = password_entry.get()
            if username in self.data['users']:
                messagebox.showerror("Error", "Username already exists")
            else:
                self.data['users'][username] = password
                save_data(self.data)
                messagebox.showinfo("Success", "User registered successfully")
                self.login_screen()

        tk.Button(self.root, text="Register", command=register, width=20).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.login_screen, width=20).pack(pady=5)

    def dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.logged_in_user}", font=("Arial", 20)).pack(pady=10)
        tk.Button(self.root, text="Add Password", command=self.add_password_screen, width=20).pack(pady=10)
        tk.Button(self.root, text="View Passwords", command=self.view_passwords, width=20).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.logout, width=20).pack(pady=5)

    def add_password_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Add Password", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.root, text="Service").pack()
        service_entry = tk.Entry(self.root)
        service_entry.pack()
        tk.Label(self.root, text="Service Username").pack()
        service_username_entry = tk.Entry(self.root)
        service_username_entry.pack()
        tk.Label(self.root, text="Service Password").pack()
        service_password_entry = tk.Entry(self.root, show="*")
        service_password_entry.pack()

        def save_password():
            service = service_entry.get()
            service_username = service_username_entry.get()
            service_password = service_password_entry.get()
            if not service or not service_username or not service_password:
                messagebox.showerror("Error", "All fields are required")
                return

            if self.logged_in_user not in self.data['passwords']:
                self.data['passwords'][self.logged_in_user] = []

            self.data['passwords'][self.logged_in_user].append({
                "service": service,
                "service_username": service_username,
                "service_password": service_password
            })

            save_data(self.data)
            messagebox.showinfo("Success", "Password saved successfully")
            self.dashboard()

        tk.Button(self.root, text="Save", command=save_password, width=20).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.dashboard, width=20).pack(pady=5)

    def view_passwords(self):
        self.clear_screen()
        tk.Label(self.root, text="Saved Passwords", font=("Arial", 20)).pack(pady=10)

        passwords = self.data['passwords'].get(self.logged_in_user, [])
        for password in passwords:
            tk.Label(self.root, text=f"Service: {password['service']}").pack()
            tk.Label(self.root, text=f"Username: {password['service_username']}").pack()
            tk.Label(self.root, text=f"Password: {password['service_password']}").pack()
            tk.Label(self.root, text="").pack()

        tk.Button(self.root, text="Back", command=self.dashboard, width=20).pack(pady=5)

    def logout(self):
        self.logged_in_user = None
        self.login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()