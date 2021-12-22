from tkinter import *
from tkinter import ttk
import sys
import tkinter.messagebox
import Functions_Crypto
import time
from Functions_Crypto import *
import EmotePannel
import ThreadReception


import DB_interaction


class FriendList(Tk):
    def __init__(self, socket, symetric_key, username, chat):
        super().__init__()
        self.title("Friend List")
        self.chat = chat

        # Make a certain color transparent (make the whole window transparent)
        # self.wm_attributes('-transparentcolor', '#17202A')

        self.private_key = DB_interaction.get_private_key(username)
        self.username = username
        self.socket = socket
        self.symetric_key_server = symetric_key

        # Center window https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens

        w = 250
        h = 500
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2) + 480
        y = (hs / 2) - 250

        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.resizable(False, False)

        friendListTitle = ttk.Label(self, text="Friend List",
                                    background='green', foreground="white",
                                    font=("Bahnschrift", 15))

        friendListTitle.place(x=80, y=2)

        # Change font on combobox https://stackoverflow.com/questions/43086378/how-to-modify-ttk-combobox-fonts

        friendList = DB_interaction.get_friends(self.username)
        text_font = ('Bahnschrift', '12')
        self.combo = ttk.Combobox(self, values=friendList, font=text_font, width=24, validate='focusout')
        # entry_box = ttk.Entry(self, font=text_font)
        self.option_add('*TCombobox*Listbox.font', text_font)
        self.combo.set("Start a conversation")
        self.combo.place(x=5, y=40)

        self.combo.bind('<Return>', lambda event: self.checkIfFriend())

        self.combo.bind('<<ComboboxSelected>>', lambda event: self.startConversation())

        Label(self, text='Add a new friend :', font=text_font).place(x=10, y=400)
        self.newFriend = Entry(self, width=20, font=text_font)
        self.newFriend.place(x=10, y=430)

        self.AddButton = Button(self, text='Add', font=('Bahnschrift', '10'))
        self.AddButton.place(x=200, y=428)

        self.ExitButton = Button(self, text='Exit', font=('Bahnschrift', '10'))
        self.ExitButton.place(x=200, y=462)

        self.AddButton.bind("<Button>", lambda e: self.addfriend())
        self.newFriend.bind('<Return>', lambda e: self.addfriend())
        self.ExitButton.bind('<Button>', lambda e: self.disconnect())

        self.number = 0
        self.socket.send("TRANSITION OK".encode("Utf8"))
        answer = self.socket.recv(255).decode("Utf8")

        if (answer != "TRANSITION OK"):
            tkinter.messagebox.showerror(title="Error", message="An unexepcted error has occured")
            sys.exit()
        self.refresh_friend_list()
        self.wait = False
        self.discussing = False
        self.mainloop()

    def refresh_friend_list(self):
        pending_requests = DB_interaction.get_friend_requests(self.username)
        for elem in pending_requests:
            action = "FRIEND_LIST_REFRESH"
            action_encr = crypt(action, self.symetric_key_server, self.private_key)
            time.sleep(0.02)
            self.socket.send(action_encr[0])
            time.sleep(0.02)
            self.socket.send(action_encr[1])
            friend_encr = crypt(elem[1], self.symetric_key_server, self.private_key)
            time.sleep(0.02)
            self.socket.send(friend_encr[0])
            time.sleep(0.02)
            self.socket.send(friend_encr[1])
            answer = self.socket.recv(1024).decode("Utf8")
            print(answer)
            if (answer == "ACCEPTED"):
                DB_interaction.add_friend(self.username, elem[1])
                DB_interaction.remove_friends_request(self.username, elem[1])

    def disconnect(self):
        action = "DISCONNECT"
        action_encr = crypt(action, self.symetric_key_server, self.private_key)
        time.sleep(0.02)
        self.socket.send(action_encr[0])
        time.sleep(0.02)
        self.socket.send(action_encr[1])
        print("Test")
        answer = self.socket.recv(1024).decode("Utf8")
        if (answer == "OK"):
            self.socket.close()
            self.chat.destroy()
            self.destroy()

    def addfriend(self):
        self.refresh_friend_list()
        if (self.newFriend.get() != "" and self.newFriend.get() != self.username and (
        not DB_interaction.already_friends(self.username, self.newFriend.get()))):
            print("Entrée de addfriend")
            request_friend_name = self.newFriend.get()
            action = "FRIEND_REQUEST"
            action_encr = crypt(action, self.symetric_key_server, self.private_key)
            time.sleep(0.02)
            self.socket.send(action_encr[0])
            time.sleep(0.02)
            self.socket.send(action_encr[1])
            time.sleep(0.02)
            friend_encr = crypt(request_friend_name, self.symetric_key_server, self.private_key)
            self.socket.send(friend_encr[0])
            time.sleep(0.02)
            self.socket.send(friend_encr[1])
            print("addfriend avant le recv")
            answer = self.socket.recv(1024).decode("Utf8")
            print(answer)
            if (answer == "ADD_FRIEND"):
                DB_interaction.add_friend(self.username, request_friend_name)
            elif (answer == "EXISTS_NOT"):
                tkinter.messagebox.showinfo(title="Warning", message="This user doesn't exist")
            else:
                DB_interaction.add_friend_request(self.username, request_friend_name)
        else:
            tkinter.messagebox.showinfo(title="Warning", message="Invalid friend name")

    def checkIfFriend(self):
        if self.combo.get() in DB_interaction.get_friends(self.username):
            self.startConversation()
        else:
            tkinter.messagebox.showerror(title="Error !", message="User not in your friend list.")

    def startConversation(self):
        action = "LOAD_HISTORY"
        action_encr =crypt(action, self.symetric_key_server, self.private_key)
        self.socket.send(action_encr[0])
        time.sleep(0.2)
        self.socket.send(action_encr[1])
        time.sleep(0.2)
        friend_encr = crypt(self.combo.get(), self.symetric_key_server, self.private_key)
        self.socket.send(friend_encr[0])
        time.sleep(0.02)
        self.socket.send(friend_encr[1])
        public_pem = self.socket.recv(2048)
        public_key = load_pem_public_key(public_pem, default_backend())
        self.chat.now_chatting(self.combo.get(), public_key)
        flag = True
        previous_encr_key = None
        sym_key = None
        message_final = ""
        while flag:
            message = ""
            print("Dans le chile flag")
            sentinel = self.socket.recv(255).decode("Utf8")
            print(sentinel)
            if(sentinel == "END"):
                flag = False
            else:
                encr_key = self.socket.recv(2048)
                if(encr_key != previous_encr_key):
                    previous_encr_key = encr_key
                    sym_key = Functions_Crypto.decrypt_asym(encr_key, self.private_key)
                encr_message = self.socket.recv(2048)
                signature = self.socket.recv(2048)
                message, validity = Functions_Crypto.decrypt(encr_message, signature, sym_key, public_key)
                if(validity == None):
                    if(sentinel == "TO"):
                        author = self.username
                        message_final = author + " : " + message
                    else:
                        author = self.combo.get()
                        message_final = author + " : " + message
                self.chat.sendMessage(message_final, False)