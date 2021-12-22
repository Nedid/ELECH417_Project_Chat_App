from tkinter import *
import socket, sys, threading, time
from LabelText import *
from ThreadClient import *

HOST, PORT = socket.gethostbyname(socket.gethostname()), 33000

"""This thread is used once, it treats all connection requests and instantiate one ThreadClient for each client attempting to
connect"""


class ThreadConnection(threading.Thread):
    def __init__(self, boss, conn):
        threading.Thread.__init__(self)
        self.connection = conn
        self.boss = boss
        self.closed = False

    def run(self):
        self.connection.listen(5)
        self.boss.updateServerActivity("Listening successfully activated.")
        while not self.closed:
            self.boss.updateServerActivity("Waiting for a client on address {0}, port {1} .".format(HOST, str(PORT)))
            new_client, address = self.connection.accept()  # Here, the thread waits for a client
            self.boss.updateServerActivity("New client detected")
            try:
                self.boss.updateServerActivity("New connection accepted : Address {0}.".format(address[0]))
                th = ThreadClient(self.boss, new_client)
                th.start()  #Here, the thread instantiate a new thread for the newcomer, this is the last time ThreadConnection thread will interact with the client
                name = th.getName()
                self.boss.addRequest(new_client, name)  #Tells the server about the new user
            except:
                print("An unexpected error occured")

    def finish(self):
        self.closed = False
        print("finish")
