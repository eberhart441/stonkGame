import customtkinter as ctk
import pandas as pd

class main(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title(f"Gloomburg Terminal")

        self._create_widgets()

    def _create_widgets(self):
        pass

class userAuth(ctk.CTk):
    def __init__(self, userData):
        super().__init__()
        self.userData = userData #dataframe with users and their data
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title(f"Gloomburg Terminal Login")

        self._create_widgets()

    def _create_widgets(self):
        self.label_title = ctk.CTkLabel(self, text="Gloomburg Terminal Login / Signup", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=20)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username")
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.entry_pass.pack(pady=10)

        self.button_login = ctk.CTkButton(self, text="Login", command=self.login)
        self.button_login.pack(pady=5)

        self.button_signup = ctk.CTkButton(self, text="Signup", command=self.signup)
        self.button_signup.pack(pady=5)

        self.label_status = ctk.CTkLabel(self, text="")
        self.label_status.pack(pady=20)

    def generate_user_id(self, length=10):
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if username in self.userData['username'].values and password in self.userData['password'].values:
            self.userData[self.userData['username'] == username] # grab the correct row
            self.label_status.configure(text=f"Welcome Back!\nUsername: {username}", text_color="green")
            self.after(1000, self.destroy)
        else:
            self.label_status.configure(text="Incorrect Auth", text_color="red")


    def signup(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if username in self.userData['username'].values:
            self.label_status.configure(text="Username already exists", text_color="red")

        else:
            user_id = self.generate_user_id()
            new_user = pd.DataFrame([[username, password, user_id, random.randint(1_000_000, 1_500_000)]], columns=['username', 'password', 'userID', 'accountMoney'])
            self.userData = pd.concat([self.userData, new_user], ignore_index=True)
            self.label_status.configure(text=f"Signup successful!\nUser ID: {user_id}", text_color="green")
            self.userData.to_csv("userData.csv")
            self.after(1000, self.destroy)

if __name__ == "__main__":
    import os
    import random

    if not os.path.exists("userData.csv") or os.stat("userData.csv").st_size == 0:
        userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
        userData.to_csv("userData.csv", index=False)
    else:
        userData = pd.read_csv("userData.csv")

        # Check if there's at least one row (excluding header)
        if userData.empty:
            userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
            userData.to_csv("userData.csv", index=False)

    authentication = userAuth(pd.read_csv("userData.csv"))
    authentication.mainloop()


    app = main()
    app.mainloop()