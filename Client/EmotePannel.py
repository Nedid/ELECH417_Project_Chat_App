from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter.messagebox import showerror

import FriendList
import DB_interaction
import ThreadReception
import Functions_Crypto
import time


class Chat(Tk):
    def __init__(self, socket, symetric_key, username):
        super().__init__()
        self.title("Chat")

        # Make a certain color transparent (make the whole window transparent)
        # self.wm_attributes('-transparentcolor', '#17202A')

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

        self.private_key = DB_interaction.get_private_key(username)
        self.username = username
        self.socket = socket
        self.symetric_key_server = symetric_key

        self.backGroundImage = PhotoImage(file="bg.png")
        self.backGroundImageLabel = Label(self, image=self.backGroundImage)
        self.backGroundImageLabel.place(x=0, y=0)

        # self.canvas=Canvas(self,width=400,height=350)
        # self.canvas.place(x=150,y=60)

        # myFont = ("Bahnschrift", 26, "bold")

        # self.chatwin=Entry(self,borderwidth=0,highlightthickness=0,font=("Bahnschrift", 18))
        # self.chatwin.place(x=20,y=20,width=660,height=380)

        self.name = username

        self.msgwin = Entry(self, borderwidth=0, highlightthickness=0, font=("Bahnschrift", 18))
        self.msgwin.place(x=20, y=420, width=660, height=32)
        self.msgwin.focus()  # Directly select the box to write a message

        self.textCons = Text(self,
                             width=20,
                             height=2,
                             bg="#212E52",
                             fg="#EAECEE",
                             font="Bahnschrift 18",
                             padx=5,
                             pady=5)
        # self.attributes('-alpha',0.5)

        self.textCons.place(relheight=0.745,
                            relwidth=0.91,
                            relx=0.03,
                            rely=0.04)

        self.buttonMsg = Button(self,
                                text="Send",
                                font="Bahnschrift 12 bold",
                                width=20,
                                bg="#fef5ff",
                                command=lambda: self.sendMessage(self.msgwin.get()))

        self.msgwin.bind('<Return>', lambda event: self.sendMessage(self.msgwin.get()))

        self.buttonMsg.place(relx=0.75,
                             rely=0.92,
                             relheight=0.06,
                             relwidth=0.22)

        self.emoteButton = Button(self,
                                  text="Emote",
                                  font="Bahnschrift 12 bold",
                                  width=20,
                                  bg="#fef5ff",
                                  command=lambda: self.openEmotePannel())

        self.emoteButton.place(relx=0.03,
                               rely=0.92,
                               relheight=0.06,
                               relwidth=0.22)

        self.FriendListButton = Button(self,
                                       text="Friend List",
                                       font="Bahnschrift 12 bold",
                                       width=20,
                                       bg="#fef5ff",
                                       command=lambda: self.openFriendList())

        self.FriendListButton.place(relx=0.39,
                                    rely=0.92,
                                    relheight=0.06,
                                    relwidth=0.22)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.place(relx=0.945,
                             rely=0.038,
                             relheight=0.745)
        self.scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)
        self.textCons.config(yscrollcommand=self.scrollbar.set)

        self.discussing = False
        self.target = None
        self.target_public_key = None
        self.personal_private_key = None
        self.sym_key_session = None
        self.sym_key_session_encr = None

        # FriendList.FriendList(self.socket, self.symetric_key_server, self.username)

    # def sendButton(self, msg):
    #     self.textCons.config(state=DISABLED)
    #     self.msg = msg
    #     self.msgwin.delete(0, END)
    #     snd = threading.Thread(target=self.sendMessage)
    #     snd.start()

    # function to send messages

    def now_chatting(self, target, public_key):
        self.discussing = True
        self.target = target
        self.target_public_key = public_key
        self.sym_key_session, self.sym_key_session_encr = Functions_Crypto.symkey_gen(public_key)

    def sendMessage(self, msg, type = True):
        self.msgwin.delete(0, END)
        self.textCons.config(state=NORMAL)
        self.textCons.insert("end", f"{self.name}: {msg}")
        self.textCons.insert("end", "\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        if(self.discussing and type):
            action = "SEND"
            action_encr, signature = Functions_Crypto.crypt(action, self.symetric_key_server, self.private_key)
            self.socket.send(action_encr)
            time.sleep(0.2)
            self.socket.send(signature)
            time.sleep(0.2)
            target_encr, signature = Functions_Crypto.crypt(self.target, self.symetric_key_server, self.private_key)
            self.socket.send(target_encr)
            time.sleep(0.2)
            self.socket.send(signature)
            time.sleep(0.2)
            msg_encr, signature = Functions_Crypto.crypt(msg, self.sym_key_session, self.private_key)
            self.socket.send(target_encr)
            time.sleep(0.2)
            self.socket.send(signature)
            time.sleep(0.2)
            self.socket.send(self.sym_key_session_encr)




    def openEmotePannel(self):
        EmotePannel()

    def openFriendList(self):
        FriendList.FriendList(self.socket, self.symetric_key_server, self.username, self)




class EmotePannel(Tk):
    def __init__(self):
        super().__init__()
        self.title("Emote pannel")

        # Make a certain color transparent (make the whole window transparent)
        # self.wm_attributes('-transparentcolor', '#17202A')

        # Center window https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens

        w = 250
        h = 250
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2) - 480
        y = (hs / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.resizable(False, False)

        # How to generate a lot of buttons from a list : https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index

        emotes = ["( ͡° ͜ʖ ͡°)", "¯\_(ツ)_/¯", "༼ つ ◕_◕ ༽つ", "ಠ_ಠ", "(ノಠ益ಠ)ノ彡┻━┻",
                  "ლ(ಠ益ಠლ)"]  # creates list to replace your actual inputs for troubleshooting purposes
        btn = []  # creates list to store the buttons ins

        for i in range(len(emotes)):  # this says for *counter* in *however many elements there are in the list files*
            # the below line creates a button and stores it in an array we can call later, it will print the value of it's own text by referencing itself from the list that the buttons are stored in
            btn.append(Button(self, text=emotes[i], font="Bahnschrift 12",
                              command=lambda c=i: self.addEmote(btn[c].cget("text")), height=1, width=15))
            btn[i].pack()  # this packs the buttons

    def addEmote(self, emote):
        # Call Chat window object
        # .msgwin.insert(END,emote)
        self.destroy()