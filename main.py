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
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title(f"Gloomburg Login")

        self._create_widgets()

    def _create_widgets(self):
        self.label_title = ctk.CTkLabel(app, text="Gloomburg Terminal Login / Signup", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=20)

        self.entry_user = ctk.CTkEntry(app, placeholder_text="Username")
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(app, placeholder_text="Password", show="*")
        self.entry_pass.pack(pady=10)

        self.button_login = ctk.CTkButton(app, text="Login", command=self.login)
        self.button_login.pack(pady=5)

        self.button_signup = ctk.CTkButton(app, text="Signup", command=self.signup)
        self.button_signup.pack(pady=5)

        self.label_status = ctk.CTkLabel(app, text="")
        self.label_status.pack(pady=20)

    def generate_user_id(self, length=10):
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def login(self):
        pass

    def signup(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        new_row = {'username': '', 'password': '', 'userID': self.generate_user_id, 'accountMoney': random.randint(1_000_000, 1_500_000)}
        pass

if __name__ == "__main__":
    import os
    import random

    if not os.path.exists("userData.csv") or os.stat("userData.csv").st_size == 0:
        df = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
        df.to_csv("userData.csv", index=False)
    else:
        df = pd.read_csv("userData.csv")

        # Check if there's at least one row (excluding header)
        if df.empty:
            df = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
            df.to_csv("userData.csv", index=False)

    authentication = userAuth()
    authentication.mainloop()

    userData = pd.read_csv("userData.csv")

    app = main()
    app.mainloop()