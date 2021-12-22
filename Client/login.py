from tkinter import *
from tkinter import font
import tkinter.messagebox
import signup
import Chat
import socket, sys
from time import *
import time
from Functions_Crypto import *
import EmotePannel

# Find host IP address https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

HOST = socket.gethostbyname(socket.gethostname())
PORT = 33000


class Login(Tk):
    def __init__(self, existant_socket=None, existant_symkey = None):
        super().__init__()
        self.title("Log in")

        # Center window https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens

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

        self.title = Label(self, text="Log in", font=("Bahnschrift", 26, "bold"))
        self.title.place(x=300, y=80)

        self.username = Label(self, text="Username", font=("Bahnschrift", 18, "bold"))
        self.username.place(x=170, y=180)

        self.password = Label(self, text="Password", font=("Bahnschrift", 18, "bold"))
        self.password.place(x=170, y=250)

        self.username = Entry(self, borderwidth=0, highlightthickness=0, font=("Bahnschrift", 18))
        self.username.place(x=300, y=183, width=235, height=32)

        self.password = Entry(self, borderwidth=0, show="*", highlightthickness=0, font=("Bahnschrift", 18))
        self.password.place(x=300, y=253, width=235, height=32)

        self.loginButtonImage = PhotoImage(file="login_button_medium.png")
        self.loginButton = Button(self, image=self.loginButtonImage, cursor="hand2", command=self.loginrequest,
                                  border=0)
        self.loginButton.place(x=270, y=320)

        self.exitButtonImage = PhotoImage(file="exit_button.png")
        self.exitButton = Button(self, image=self.exitButtonImage, cursor="hand2", command=self.Exit,
                                  border=0)
        self.exitButton.place(x=0, y=0)

        self.signintext = Label(self, text="You do not have an account yet?", font=("Bahnschrift", 12))
        self.signintext.place(x=210, y=385)
        self.signin = Label(self, text="Sign up", cursor="hand2", foreground="blue",
                            font=("Bahnschrift", 12, 'underline'))
        self.signin.place(x=445, y=385)
        self.signin.bind("<Button>", lambda e: self.SignUp())

        self.username.bind('<Return>', lambda event: self.password.focus())
        self.password.bind('<Return>', lambda event: self.loginrequest())

        if existant_socket == None:
            self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socketConnection.connect((HOST, PORT))
            except socket.error:
                tkinter.messagebox.showerror(title="Error", message="The server in unreachable, the program will close")
                sys.exit()
            welcomeMessage = self.socketConnection.recv(255).decode("Utf8")
            public_pem = self.socketConnection.recv(1024)
            self.public_key_server = load_pem_public_key(public_pem, default_backend())
            self.initial_symkey, initial_encrypted_symkey = symkey_gen(self.public_key_server)
            self.socketConnection.send(initial_encrypted_symkey)
            print(self.initial_symkey)
            # tkinter.messagebox.showinfo(title="Success !", message=welcomeMessage)

        else:
            self.socketConnection = existant_socket
            self.initial_symkey = existant_symkey

        self.mainloop()

    def loginrequest(self):
        first = encrypt_sym("LOGIN", self.initial_symkey)
        # self.socketConnection.send("LOGIN".encode("Utf8"))
        self.socketConnection.send(first)
        time.sleep(0.01)
        self.socketConnection.send(encrypt_sym(self.username.get(), self.initial_symkey))
        time.sleep(0.01)
        self.socketConnection.send(encrypt_sym(self.password.get(), self.initial_symkey))
        answer = self.socketConnection.recv(255).decode("Utf8")
        if (answer == "VALID"):
            socket = self.socketConnection
            key = self.initial_symkey
            username = self.username.get()
            self.destroy()
            EmotePannel.Chat(socket, key, username)
        else:
            tkinter.messagebox.showerror(title="Error !", message="Wrong password or wrong username (or both)")

    def SignUp(self):
        socket = self.socketConnection
        self.destroy()
        signup.Signup(socket, self.initial_symkey)

    def Exit(self):
        self.destroy()