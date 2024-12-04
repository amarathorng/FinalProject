import tkinter as tk
from tkinter import messagebox, Toplevel
from datetime import datetime
import sqlite3
from tkinter import Toplevel
from tkinter import ttk

def connect_to_database():
    conn = sqlite3.connect("task.db")
    return conn
def create_tasks_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

CREDENTIALS = {"username": "Admin", "password": "270305"}

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("350x300")
        self.root.configure(bg="#ffcccb")

        self.title_label = tk.Label(self.root, text="To-Do List App", font=("Comic Sans MS", 16, "bold"), bg="#ffcccb")
        self.title_label.pack(pady=10)

        tk.Label(self.root, text="Username", font=("Arial", 12, "bold")).pack(pady=5)
        self.username_entry = tk.Entry(self.root, font=("Arial", 12))
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password", font=("Arial", 12, "bold")).pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self.root, text="Login", command=self.check_login, font=("Arial", 12), bg="lightblue")
        self.login_button.pack(pady=20)

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == CREDENTIALS["username"] and password == CREDENTIALS["password"]:
            messagebox.showinfo("Login Success", "Welcome to the To-Do List App!")
            self.root.destroy()

            todo_root = tk.Tk()
            TodoApp(todo_root)
            todo_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("450x600")
        self.root.configure(bg="lightcoral")

        self.title_label = tk.Label(self.root, text="To-Do List App", font=("Comic Sans MS", 16, "bold"), bg="lightcoral")
        self.title_label.pack(pady=(10, 0))

        self.input_frame = tk.Frame(self.root, bg="lightpink")
        self.input_frame.pack(pady=10)

        self.task_entry = tk.Entry(self.input_frame, width=20, font=("Arial", 14), bd=2, bg="lightblue", relief=tk.GROOVE)
        self.task_entry.grid(row=0, column=0, padx=(0, 5))

        self.add_button = tk.Button(self.input_frame, text="Add Task", command=self.add_task, bg="pink", fg="white", font=("Helvetica", 14), bd=2, relief=tk.GROOVE)
        self.add_button.grid(row=0, column=1, padx=(5, 0))

        self.tasks_listbox = tk.Listbox(self.root, font=("Arial", 14), bd=2, bg="lightblue", relief=tk.GROOVE, selectmode=tk.SINGLE)
        self.tasks_listbox.pack(padx=10, pady=(10, 0), expand=True, fill=tk.BOTH)

        self.action_frame = tk.Frame(self.root, bg="lightcoral")
        self.action_frame.pack(pady=10)

        self.mark_complete_button = tk.Button(self.action_frame, text="Mark as Complete", command=self.mark_as_complete, bg="green", fg="white", font=("Helvetica", 12), bd=2, relief=tk.GROOVE)
        self.mark_complete_button.grid(row=0, column=0, padx=5)

        self.remove_button = tk.Button(self.action_frame, text="Remove Task", command=self.remove_task, bg="red", fg="white", font=("Helvetica", 12), bd=2, relief=tk.GROOVE)
        self.remove_button.grid(row=0, column=1, padx=5)

        self.review_button = tk.Button(self.root, text="Review Tasks", command=self.open_review_window, bg="blue", fg="white", font=("Helvetica", 12), bd=2, relief=tk.GROOVE)
        self.review_button.pack(pady=10)

        self.review_button = tk.Button(self.root, text="Review Tasks", command=self.open_review_tasks, bg="orange", fg="white", font=("Helvetica", 12), bd=2, relief=tk.GROOVE)
        self.review_button.pack(pady=10)

        self.load_tasks()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            now = datetime.now()
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task, date, time, status) VALUES (?, ?, ?, ?)",
                           (task, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), "Incomplete"))
            conn.commit()
            conn.close()
            self.load_tasks()
            self.task_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Task added successfully!")
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def mark_as_complete(self):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            task_id = self.tasks[selected_index[0]]["id"]
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ("Complete", task_id))
            conn.commit()
            conn.close()
            self.load_tasks()
            messagebox.showinfo("Success", "Task marked as complete!")
        else:
            messagebox.showwarning("Warning", "You must select a task to mark as complete.")

    def remove_task(self):
        selected_index = self.tasks_listbox.curselection()
        if selected_index:
            task_id = self.tasks[selected_index[0]]["id"]
            confirm = messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this task?")
            if confirm:
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                conn.close()
                self.load_tasks()
                messagebox.showinfo("Success", "Task removed successfully!")
        else:
            messagebox.showwarning("Warning", "You must select a task to remove.")

    def load_tasks(self):
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        self.tasks = [{"id": row[0], "task": row[1], "date": row[2], "time": row[3], "status": row[4]} for row in cursor.fetchall()]
        conn.close()
        self.update_tasks_listbox()

    def update_tasks_listbox(self):
        self.tasks_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_text = f"{task['task']} ({task['status']})"
            self.tasks_listbox.insert(tk.END, task_text)

    def open_review_window(self):
        ReviewTasks()

class ReviewTasks:
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Review Tasks")
        self.window.geometry("700x400")
        self.window.configure(bg="lightpink")

        tk.Label(self.window, text="All Tasks", font=("Arial", 16, "bold"), bg="lightpink").pack(pady=10)

        self.tree = ttk.Treeview(self.window, columns=("ID", "Task", "Date", "Time", "Status"), show="headings", height=15)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=50)
        self.tree.column("Task", width=250)
        self.tree.column("Date", width=100)
        self.tree.column("Time", width=100)
        self.tree.column("Status", width=100)

        self.load_tasks()

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, date, time, status FROM tasks")
        tasks = cursor.fetchall()
        conn.close()

        for task in tasks:
            self.tree.insert("", "end", values=task)

        self.load_tasks()

    def load_tasks(self):
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT task, date, time, status FROM tasks")
        tasks = cursor.fetchall()
        conn.close()

        for task in tasks:
            self.tree.insert("", "end", values=task)


    def load_tasks(self):
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = [{"task": row[1], "date": row[2], "time": row[3], "status": row[4]} for row in cursor.fetchall()]
        conn.close()

        self.tasks_listbox.delete(0, tk.END)
        for task in tasks:
            task_text = f"{task['task']} - {task['date']} {task['time']} ({task['status']})"
            self.tasks_listbox.insert(tk.END, task_text)

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, date, time, status FROM tasks")
        tasks = cursor.fetchall()  # Fetch all tasks
        conn.close()

        print("Tasks retrieved from database:", tasks)

        for task in tasks:
            self.tree.insert("", "end", values=task)

if __name__ == "__main__":
    create_tasks_table()
    login_root = tk.Tk()
    LoginApp(login_root)
    login_root.mainloop()

