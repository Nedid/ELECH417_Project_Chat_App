import sqlite3
import Functions_Crypto
from Functions_Crypto import *

def check_username_validity(username):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = '{0}'".format(username))
    if(len(list(cur)) == 0):
        conn.close()
        return True
    else:
        conn.close()
        return False

def add_message_in_history(username, target, sym_key , message, signature):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM history ORDER BY id DESC")
    liste = list(cur)
    if (len(liste) != 0):
        id = liste[0][0] + 1
    else:
        id = 1
    data = [username, target, sym_key, message, id, signature]
    cur.execute("INSERT INTO history(username, target, sym_key, message,id, signature) VALUES(?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

def create_user_account(username, password, public_key):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY user_id DESC")
    liste = list(cur)
    if(len(liste) != 0):
        id = liste[0][0] + 1
    else:
        id = 1
    data = (id, username, password, public_key.decode("Utf8"))
    cur.execute("INSERT INTO users(user_id, username, password, public_key) VALUES(?,?,?,?)",data)
    conn.commit()
    conn.close()

def get_history(username, target):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE (username='{0}' AND target = '{1}') ORDER BY id".format(username,target))
    data = list(cur)
    conn.close()
    return data

def check_password(username, password):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username='{0}'".format(username))
    data = list(cur)
    if(len(data) == 0):
        conn.close()
        return False
    elif(len(data) == 1):
        if data[0][2] == password:
            conn.close()
            return True
        else:
            conn.close()
            return False
    else:
        conn.close()
        return False

def get_public_key(username):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username='{0}'".format(username))
    data = list(cur)
    key = data[0][3].encode("Utf8")
    conn.close()
    return load_pem_public_key(key, default_backend())

def user_exists(username):
    return not check_username_validity(username)

def has_been_asked_friends(username, target):
    print("Dans has_been_asked_friends")
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM friends_requests WHERE asker='{0}'".format(target))
    data = list(cur)
    for element in data:
        if(element[1] == username):
            cur.execute("DELETE FROM friends_requests WHERE (asker = '{0}' AND asked  = '{1}') ".format(target, username))
            conn.commit()
            conn.close()
            print("Dans has_been_asked_friends TRUE")
            return True
    conn.close()
    return False

def add_friends_request(asker, asked):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    if(not check_friend_request(asker, asked)):
        data = (asker, asked)
        cur.execute("INSERT INTO friends_requests(asker, asked) VALUES(?,?)",data)
        conn.commit()
    conn.close()

def check_friend_request(username, target):
    conn = sqlite3.connect("DB_SERVER.sq3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM friends_requests WHERE asker = '{0}'".format(username))
    data = list(cur)
    conn.close()
    for elem in data:
        if elem[1] == target:
            return True
    return False


if __name__ == '__main__':
    conn = sqlite3.connect("DB_SERVER.sq3")
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