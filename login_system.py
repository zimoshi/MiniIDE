import sqlite3
import tkinter as tk
from tkinter import messagebox

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



def get_role(username):
    if username.endswith("*"):
        return "Admin"
    elif username.endswith("^"):
        return "Developer"
    return "User"

def authenticate(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    # print(result[0])
    if result and result[0] == password:
        return True, get_role(username)
    return False, None

class LoginSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniIDE Login")
        self.root.geometry("300x200")

        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=10)
        self.username_entry.insert(0, "Username")

        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=10)
        self.password_entry.insert(0, "Password")

        login_button = tk.Button(root, text="Login", command=self.check_login)
        login_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            ok, role = authenticate(username, password)
            if ok:
                self.root.destroy()
                import minieditor
                minieditor.MiniIDE(role, username).mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        else:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")

if __name__ == "__main__":
    init_db()
    # add_users()
    root = tk.Tk()
    app = LoginSystem(root)
    root.mainloop()
