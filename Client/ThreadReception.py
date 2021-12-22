import socket, sys, threading
from Functions_Crypto import *


class ThreadReception(threading.Thread):
    def __init__(self, connection, sym_key_friend, public_key_friend, boss, friend_name):
        threading.Thread.__init__(self)
        self.server = connection
        self.sym_key_friend = sym_key_friend
        self.public_key_signature = public_key_friend
        self.boss = boss
        self.friend_name = friend_name
        print("Création du thread réception")

    def run(self):
        stop = False
        while not stop:
            print("Thread réception attend")
            message_encr = self.server.recv(2048)
            signature = self.server.recv(2048)
            if (message_encr.decode("Utf8") == "END_CONVERSATION"):
                stop = True
                self.boss.end_discussion()
            else:
                message, validity = decrypt(message_encr, signature, self.sym_key_friend, self.public_key_signature)
                if(validity == None):
                    self.boss.sendMessage(self.friend_name + " : " + message, False)