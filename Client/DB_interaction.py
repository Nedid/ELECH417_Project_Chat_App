import sqlite3

from cryptography.hazmat.primitives.serialization import load_pem_private_key

import Functions_Crypto
import time
from Functions_Crypto import *

def enreg_keys_account(username, public_key, private_key):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_str = public_pem.decode("Utf8")
    private_str = private_pem.decode("Utf8")
    data = (username, public_str, private_str)
    cur.execute("INSERT INTO accounts(username, public_key, provate_key) VALUES(?,?,?)", data)
    conn.commit()
    conn.close()

def get_private_key(username):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username = '{0}'".format(username))
    data = list(cur)
    if(len(data) == 1):
        key = bytes(data[0][2].encode("Utf8"))
        private_key = load_pem_private_key(key,None,default_backend())
        return private_key
    else:
        raise RuntimeError

def get_public_key(username):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username = '{0}'".format(username))
    data = list(cur)
    if(len(data) == 1):
        key = bytes(data[0][1].encode("Utf8"))
        public_key = load_pem_public_key(key, default_backend())
        return public_key
    else:
        raise RuntimeError

def add_friend(username, friend):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    data = (username, friend)
    cur.execute("INSERT INTO friends_list(account, friend) VALUES(?,?)", data)
    conn.commit()
    conn.close()

def already_friends(account, friend):
    friend_list = get_friends(account)
    if(friend in friend_list):
        return True
    else:
        return False


def already_in_friend_request(username, friend):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM friends_requests_list WHERE account = '{0}'".format(username))
    data = list(cur)
    conn.close()
    for elem in data:
        if(elem[1] == friend):
            return True
    return False


def add_friend_request(username, friend):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    if not already_in_friend_request(username, friend):
        data = (username, friend)
        cur.execute("INSERT INTO friends_requests_list(account, friend) VALUES(?,?)", data)
        conn.commit()
    conn.close()

def remove_friends_request(username, friend):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("DELETE FROM friends_requests_list WHERE (account = '{0}' AND friend = '{1}')".format(username, friend))
    conn.commit()
    conn.close()


def get_friend_requests(username):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM friends_requests_list WHERE account = '{0}'".format(username))
    data = list(cur)
    conn.close()
    return data

def get_friends(username):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM friends_list WHERE account = '{0}'".format(username))
    data = list(cur)
    friends = []
    for elem in data:
        friends.append(elem[1])
    conn.close()
    return friends

def remove_friend_request(account, request):
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    cur.execute("DELETE FROM friends_requests_list WHERE (account = '{0}' AND friend = '{1}')".format(account, request))

if __name__ == '__main__':
    conn = sqlite3.connect("DB_CLIENT.sq3")
    cur = conn.cursor()
    while 1:
        print("Veuillez entrer votre requête SQL (ou <Enter> pour terminer) :")
        requete = input()
        if requete == "":
            break
        try:
            cur.execute(requete)
        except :
            print("***Requête SQL incorrecte***")
        else:
            for enreg in cur:
                print(enreg)
        print()
    choix = input("Confirmez-vous l'enregistrement de l'état actuel ? (o/n)")
    if(len(choix) != 0 and (choix[0] == 'o' or choix[0] == 'O')):
        conn.commit()
    else:
        conn.close()