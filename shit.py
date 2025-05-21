import customtkinter as ctk

# Setup window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x400")
app.title("Login / Signup")

users = {}  # Just a dictionary to store usernames and passwords

def login():
    username = entry_user.get()
    password = entry_pass.get()
    if username in users and users[username] == password:
        label_status.configure(text="Login successful", text_color="green")
    else:
        label_status.configure(text="Login failed", text_color="red")

def signup():
    username = entry_user.get()
    password = entry_pass.get()
    if username in users:
        label_status.configure(text="User already exists", text_color="orange")
    else:
        users[username] = password
        label_status.configure(text="Signup successful", text_color="green")

# Widgets
label_title = ctk.CTkLabel(app, text="Login / Signup", font=ctk.CTkFont(size=20, weight="bold"))
label_title.pack(pady=20)

entry_user = ctk.CTkEntry(app, placeholder_text="Username")
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(app, placeholder_text="Password", show="*")
entry_pass.pack(pady=10)

button_login = ctk.CTkButton(app, text="Login", command=login)
button_login.pack(pady=5)

button_signup = ctk.CTkButton(app, text="Signup", command=signup)
button_signup.pack(pady=5)

label_status = ctk.CTkLabel(app, text="")
label_status.pack(pady=20)

app.mainloop()
