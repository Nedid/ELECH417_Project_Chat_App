from tkinter import *
import socket, sys, threading, time
from ThreadConnection import *
from LabelText import *
from Functions_Crypto import *

HOST, PORT = socket.gethostbyname(socket.gethostname()), 33000


class FenServer(Tk):
    def __init__(self):
        """Creation of the window of the server"""
        Tk.__init__(self)
        self.listening = None
        self.serverOpened = False  # Variable uses to know if the clients can or can't connect to the server
        self.box1 = LabelText(self, "Activity :", "")
        self.box1.grid(row=1, column=1, rowspan=3, columnspan=3)
        self.box2 = LabelText(self, "Admin commands :", "")     #Label text are peronalised widget, used to display informations about the server
        self.box2.grid(row=1, column=4, rowspan=3, columnspan=3)
        Label(self, text="Enter a command : ").grid(row=4, column=1, columnspan=3)
        self.command = Entry(self)
        self.command.grid(row=4, column=4, columnspan=3)
        Button(self, text="Quit", command=self.close).grid(row=5, column=1, columnspan=1)
        self.buttonOpenServer = Button(self, text="Open server", command=self.openServer)
        self.buttonOpenServer.grid(row=5, column=2, columnspan=1)
        Button(self, text="Close server", command=self.closeServer).grid(row=5, column=3, columnspan=1)
        Button(self, text="Clear terminals", command=self.clearTerminals).grid(row=5, column=4, columnspan=1)
        Button(self, text="Execute command", command=self.executeCommand).grid(row=5, column=5, columnspan=2)
        self.requestConn = {}   #Dictionary used to keep in memory the clients not authentified yet
        self.connClient = {}    #Dictionary used to keep in memory the clients connected to an account
        self.waitingForConversation = {}

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.public_key, self.private_key = asymkey_gen()  #Generation of the pair of public and private keys, this pair change evry time the server is launched

        self.mainloop()

    def is_already_waiting(self,user, target):
        if not (user in self.waitingForConversation):
            return False
        elif self.waitingForConversation[user] == target:
            return True
        else:
            return False

    def get_destination_connection(self, destination_username):
        return self.connClient[destination_username]

    def is_now_waiting(self,user, target):
        self.waitingForConversation[user] = target
        print("{0} attend désormais {1}".format(user, target))

    def not_waiting_anymore(self, user, target):
        print("Dans le not waiting anymore")
        if(user in self.waitingForConversation):
            if(self.waitingForConversation[user] == target):
                del self.waitingForConversation[user]
                print("{0} n'attend plus {1}".format(user, target))
            else:
                raise RuntimeError

    def addConnected(self, new_conn, it, name):
        """When a  user enters a correct password, he is removed from the requestConn dictionary and
        added to the connClient dictionary, this allows to keep in memory all the users currently connected"""
        del self.requestConn[name]
        self.connClient[it] = new_conn

    def get_socket_username(self, username):

        return self.connClient[username]

    def is_connected(self, username):
        """Check if a given user is connected"""
        return username in self.connClient

    def disconnect_user(self, username):
        """Function called when a client disconnect, it removes him from the list of the connected users"""
        del self.connClient[username]

    def close(self):
        if (self.listening != None):
            self.listening.finish()
        self.destroy()

    def clearTerminals(self):
        """This function clears both terminals of the server"""
        self.box1.clear_display()
        self.box2.clear_display()

    def executeCommand(self):
        """Allows an administrator to type sepcial commands to the server (i.e. : acces to the database)"""
        com = self.command.get()
        self.box2.update_display(str(self.is_connected(com)))
        self.box2.update_display(com)
        self.box2.update_display(str(len(self.requestConn)))

    def openServer(self):
        """Very important function that opens the server"""
        if not self.serverOpened:
            try:
                self.connection.bind((HOST, PORT))
                self.box1.update_display("Server sucessfully opened on host {0}, port {1}.".format(HOST, str(PORT)))
                self.serverOpened = True
                try:
                    self.listening = ThreadConnection(self, self.connection) #Launch the ThreadConnection, this thread is launched once and treats all the connections requests
                    self.listening.start() #start the thread
                except:
                    self.box1.update_display("Launching thread connection failed")
            except socket.error:
                self.box1.update_display("Socket creation failed")
        else:
            self.box1.update_display("The server is already opened")

    def closeServer(self):
        if self.serverOpened:
            try:
                self.box1.update_display("Server sucessfully closed")
                self.serverOpened = False
            except socket.error:
                self.box1.update_display("Socket closing failed")
        else:
            self.box1.update_display("The server is already closed")

    def updateServerActivity(self, message):
        """Called exclusively by the different threads, this function is used to display data on the left terminal"""
        self.box1.update_display(message)

    def addRequest(self, new_conn, it):
        """Function called when any person execute the client software, to keep in memory who is attempting to connect"""
        self.requestConn[it] = new_conn

    def get_public_key(self):
        """Return the public key of the server"""
        return self.public_key

    def get_private_key(self):
        """Return the private key of the server. Of course, the private key is never used outside of the server"""
        return self.private_key


if __name__ == '__main__':
    fen = FenServer()

    fen.mainloop()
