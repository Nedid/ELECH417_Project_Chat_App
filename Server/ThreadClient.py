from tkinter import *
import socket, sys, threading, time
from LabelText import *
import time
from sqlite3 import *
import DB_Interaction
from Functions_Crypto import *
import random

"""This thread is used for the communication between a given client and the server, every client has its own ThreadClient and every
ThreaClient only interacts with one user. """


class ThreadClient(threading.Thread):
    def __init__(self, boss, conn):
        threading.Thread.__init__(self)
        self.connection = conn
        self.boss = boss
        self.active = True
        self.destination = None
        print(conn)

    def run(self):
        name = self.getName()
        while self.active:
            connected = False
            self.connection.send("Message from dedicated thread, welcome {0}".format(name).encode("Utf8"))

            """Here, the first important step is to send the public key of the server to the new client, this public key
            will be used by the client to generate an encrypted symmetric key that will be used for further communication
            between the client and the server"""
            public = self.boss.get_public_key()
            public_pem = public.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.connection.send(public_pem)  # Sending of the public key of the server to the client

            initial_symetric_key_encrypted = self.connection.recv(1024)
            initial_symetric_key = decrypt_asym(initial_symetric_key_encrypted, self.boss.get_private_key())
            username = ""
            while not connected and self.active:
                action_encr = self.connection.recv(255)
                action = decrypt_sym(action_encr, initial_symetric_key)
                self.boss.updateServerActivity(action)
                if action == "REGISTER":
                    print("Dans le register")
                    self.register_action(initial_symetric_key)
                elif action == "LOGIN":
                    connected, username = self.login_action(initial_symetric_key)
                else:
                    time.sleep(5)
            while self.active:
                """We get to this part of the code once the useer in authentifie"""
                self.boss.addConnected(self.connection, username, self.name) #Add the connected user to the dictionnary of all connected users
                self.connection.send("TRANSITION OK".encode("Utf8"))    #Tells the client that the transition to the "main" part was a success
                answer = self.connection.recv(255).decode("Utf8")   #Check if everything is okay for the client
                if (answer == "TRANSITION OK"):
                    self.boss.updateServerActivity("User {0} connected".format(username))   #Display the new client on the console
                    """From here, the communication between a client and the server will work as follows : the client will send a specific action as first messsage
                    and will sign it, the server will decode the action and go in the desired state before waiting for further informations from the client"""
                    while self.active:
                        action_encr = self.connection.recv(1024)
                        signature = self.connection.recv(1024)
                        action, flag = decrypt(action_encr, signature, initial_symetric_key,
                                               DB_Interaction.get_public_key(username))
                        if (flag == None):
                            if (action == "FRIEND_REQUEST"):
                                """When a user wants to add a new friend, this is the state of the server"""
                                target_encr = self.connection.recv(1024)
                                signature = self.connection.recv(1024)
                                target, flag = decrypt(target_encr, signature, initial_symetric_key,
                                                       DB_Interaction.get_public_key(username))
                                if (DB_Interaction.user_exists(target)):
                                    if (DB_Interaction.has_been_asked_friends(username, target)):
                                        """If the desired friend exists and had already added the user as friends, then the
                                        server tells the user it can add the new friend"""
                                        DB_Interaction.add_friends_request(target, username)
                                        self.connection.send("ADD_FRIEND".encode("Utf8"))
                                    else:
                                        """If the desired friend exists and but hasn't added the user as friends yet, then the
                                            server tells the user it has to add the friend to the friends_requsts_list located
                                             on the client side"""
                                        DB_Interaction.add_friends_request(username, target)
                                        self.connection.send("ADD_REQUEST".encode("Utf8"))
                                else:
                                    """If the user doens't exist, the server tells the user"""
                                    self.connection.send("EXISTS_NOT".encode("Utf8"))
                            elif (action == "FRIEND_LIST_REFRESH"):
                                """This state is used to check if a given friend request has been "accepted" by the
                                target"""
                                target_encr = self.connection.recv(1024)
                                signature = self.connection.recv(1024)
                                target, flag = decrypt(target_encr, signature, initial_symetric_key,
                                                       DB_Interaction.get_public_key(username))
                                if (flag == None):
                                    if (DB_Interaction.check_friend_request(target, username)):
                                        self.connection.send("NOT_ACCEPTED".encode("Utf8"))
                                    else:
                                        self.connection.send("ACCEPTED".encode("Utf8"))
                                else:
                                    self.connection.send("ERROR".encode("Utf8"))
                            elif (action == "DISCONNECT"):
                                """Tells the server that the user wants to disconnect"""
                                self.active = False
                                self.connection.send("OK".encode("Utf8"))
                            elif (action == "LOAD_HISTORY"):
                                """This state sends the message history with a specific friend to the user.
                                the old messages are stored encrypted with the signature, and everything needed to retrieve
                                the original message (specific symetric key used for this message), the friend's public key is stored
                                in another databse and sent to the user at the beginning of the process"""
                                target_encr = self.connection.recv(1024)
                                signature = self.connection.recv(1024)
                                target, flag = decrypt(target_encr, signature, initial_symetric_key,
                                                       DB_Interaction.get_public_key(username))
                                data_to = DB_Interaction.get_history(username, target)
                                data_from = DB_Interaction.get_history(target, username)
                                public_pem = DB_Interaction.get_public_key(target).public_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                                )
                                self.connection.send(public_pem)
                                i = 0
                                j = 0
                                for k in range (0,len(data_from)+len(data_to)):
                                    print(len(data_from)+len(data_to))
                                    """Send every old messages until there is noe message anymore, et at that moment, the
                                    server send END, which will trigger the end of a loop on client side"""
                                    time.sleep(0.2)
                                    if(len(data_to) != 0 and len(data_from) != 0):
                                        if(i >= len(data_from)):
                                            i = i-1
                                        if(j >= len(data_to)):
                                            j = j - 1
                                        if(data_from[i][4] < data_to[j][4]):
                                            print("datafrom")
                                            self.connection.send("FROM".encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_from[i][2].encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_from[i][3].encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_from[j][5].encode("Utf8"))
                                            i = i + 1
                                        else:#CREATE TABLE history(username TEXT, target TEXT, sym_key TEXT, message TEXT, id INTEGER)
                                            self.connection.send("TO".encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_to[j][2].encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_to[j][3].encode("Utf8"))
                                            time.sleep(0.2)
                                            self.connection.send(data_to[j][5].encode('Utf8'))
                                            j = j + 1
                                    elif(len(data_to) != 0 and len(data_from) == 0):
                                        
                                self.connection.send("END".encode("Utf8"))
                            elif(action == "SEND"):
                                print("Dans action")
                                target_encr = self.connection.recv(1024)
                                signature = self.connection.recv(1024)
                                target, flag = decrypt(target_encr, signature, initial_symetric_key,
                                                       DB_Interaction.get_public_key(username))
                                print("après les recv")
                                message_encr = self.connection.recv(2048).decode("Utf8")
                                signature = str(self.connection.recv(2048))
                                sym_key = str(self.connection.recv(2048))
                                DB_Interaction.add_message_in_history(username, target,sym_key, message_encr, signature)
                                print("Fin SEND")

                        else:
                            self.connection.send("ERROR".encode("Utf8"))
                        time.sleep(0.2)
                else:
                    self.boss.updateServerActivity("Error 001")
                    self.active = False
            self.boss.updateServerActivity("User {0} disconnected".format(username))
            self.boss.disconnect_user(username)
            self.connection.close()


    def register_action(self, initial_symetric_key):
        """This method is called when a user creates a new account
        The first step is to check if the username is already used or not, if it is then the creation doens't """
        username_encr = self.connection.recv(1024)
        password_encr = self.connection.recv(1024)
        username = decrypt_sym(username_encr, initial_symetric_key)
        password = decrypt_sym(password_encr, initial_symetric_key)
        self.boss.updateServerActivity(username)
        self.boss.updateServerActivity(password)
        if (DB_Interaction.check_username_validity(username)):
            self.connection.send("VALID".encode("Utf8"))
            self.create_new_account(username, password)
        else:
            self.connection.send("ERR".encode("Utf8"))

    def create_new_account(self, username, password):
        public_pem = self.connection.recv(2048)
        DB_Interaction.create_user_account(username, password, public_pem)

    def login_action(self, initial_symetric_key):
        print("Dans la login action")
        username_encr = self.connection.recv(1024)
        username = decrypt_sym(username_encr, initial_symetric_key)
        password_encr = self.connection.recv(1024)
        password = decrypt_sym(password_encr, initial_symetric_key)
        self.boss.updateServerActivity("Tentative de connexion")
        if (DB_Interaction.check_password(username, password)):
            self.boss.updateServerActivity("Connexion valide")
            self.connection.send("VALID".encode("Utf8"))
            return True, username
            # Update user actif dans self.boss
        else:
            self.boss.updateServerActivity("Connexion invalide")
            self.connection.send("ERR".encode("Utf8"))
            return False, ""
