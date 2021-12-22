from tkinter import *
from tkinter import font
import tkinter.messagebox
import login
import Chat
import socket, sys
from time import *
import time
from Functions_Crypto import *
from DB_interaction import *
import DB_interaction


# Find host IP address https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

HOST = socket.gethostbyname(socket.gethostname())
PORT = 33000

class Signup(Tk):
    def __init__(self, socket, sym_key):
        super().__init__()
        self.title("Sign up")

        w = 700
        h = 500
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.resizable(False, False)

        self.backGroundImage = PhotoImage(file="bg.png")
        self.backGroundImageLabel = Label(self, image=self.backGroundImage)
        self.backGroundImageLabel.place(x=0, y=0)

        self.canvas = Canvas(self, width=400, height=350)
        self.canvas.place(x=150, y=60)

        # myFont = ("Bahnschrift", 26, "bold")

        self.title = Label(self, text="Sign up", font=("Bahnschrift", 26, "bold"))
        self.title.place(x=290, y=80)

        self.username = Label(self, text="Username", font=("Bahnschrift", 18, "bold"))
        self.username.place(x=170, y=180)

        self.password = Label(self, text="Password", font=("Bahnschrift", 18, "bold"))
        self.password.place(x=170, y=250)

        self.username = Entry(self, borderwidth=0, highlightthickness=0, font=("Bahnschrift", 18))
        self.username.place(x=300, y=183, width=235, height=32)

        self.password = Entry(self, borderwidth=0, show="*", highlightthickness=0, font=("Bahnschrift", 18))
        self.password.place(x=300, y=253, width=235, height=32)

        self.loginButtonImage = PhotoImage(file="login_button_medium.png")
        self.loginButton = Button(self, image=self.loginButtonImage, cursor="hand2", command=self.signuprequest,
                                  border=0)
        self.loginButton.place(x=270, y=320)

        self.signintext = Label(self, text="You already have an account?", font=("Bahnschrift", 12))
        self.signintext.place(x=215, y=385)
        self.signin = Label(self, text="Log in", cursor="hand2", foreground="blue",
                            font=("Bahnschrift", 12, 'underline'))
        self.signin.place(x=435, y=385)
        self.signin.bind("<Button>", lambda e: self.Login(socket))

        self.initial_symkey = sym_key
        self.socket = socket
        self.mainloop()

    def Login(self, socket):
        # Display log in window
        sockett = self.socket
        key = self.initial_symkey
        self.destroy()
        login.Login(sockett,key)

    def signuprequest(self):
        first = encrypt_sym("REGISTER", self.initial_symkey)
        # self.socket.send("REGISTER".encode("Utf8"))
        self.socket.send(first)
        time.sleep(0.01)
        self.socket.send(encrypt_sym(self.username.get(), self.initial_symkey))
        time.sleep(0.01)
        self.socket.send(encrypt_sym(self.password.get(), self.initial_symkey))
        answer = self.socket.recv(255).decode("Utf8")
        if (answer == "VALID"):
            tkinter.messagebox.showinfo(title="Success !", message="Informations are valid")
            self.create_account(self.username.get(), self.password.get())
        else:
            tkinter.messagebox.showerror(title="Error", message="This username is already used")

    def create_account(self, u_n, password):
        public_key, private_key = asymkey_gen()
        DB_interaction.enreg_keys_account(u_n, public_key, private_key)
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.socket.send(public_pem)
        print("Create account")
