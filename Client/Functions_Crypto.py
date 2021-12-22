from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from cryptography.fernet import Fernet


def symkey_gen(public_key):  # Crée la clé symmétrique, et renvoie également la clé symmétrique encryptée
    symkey = Fernet.generate_key()
    encrypted_symkey = public_key.encrypt(symkey, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                                               algorithm=hashes.SHA1(), label=None))
    return symkey, encrypted_symkey


def encrypt_sym(msg, symkey):  # Encrypte le message via la clé symétrique après l'avoir encodé
    return Fernet(symkey).encrypt(msg.encode('Utf8'))


def decrypt_sym(token, symkey):  # Decrypte et decode le message
    return Fernet(symkey).decrypt(token).decode('Utf8')


def asymkey_gen():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
    public_key = private_key.public_key()
    return public_key, private_key


def encrypt_asym(msg, public_key):
    return public_key.encrypt(msg, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(),
                                                label=None))


def decrypt_asym(encrypted_symkey, private_key):  # Décrypte la clé symétrique
    return private_key.decrypt(encrypted_symkey,
                               padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(),
                                            label=None))

def crypt(message, sym_key, private_key):
    crypt_msg = Fernet(sym_key).encrypt(message.encode('Utf8')) #Encrypte le message via une clé symmétrique
    signature = private_key.sign(message.encode('Utf8'),padding.PSS(mgf=padding.MGF1(hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA1()) #Signe le message, en encryptant le hash (créé via l'algorithme SHA-1) avec une clé privée
    return crypt_msg, signature

def decrypt(token, signature, sym_key, public_key):
    decrypted_token = Fernet(sym_key).decrypt(token) #Message décrypté
    msg = decrypted_token.decode('Utf8') #Message décodé, remis sous forme de string
    try :
        verif = public_key.verify(signature, decrypted_token, padding.PSS(mgf=padding.MGF1(hashes.SHA1()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA1()) #Vérification de l'intégrité du message
    except :
        verif = False #Si la signature ne correspond pas au message et trigger une exception, la fonction renvoie un false
    return msg, verif


def removeBEGIN_END(key_bytes):
    key_str = str(key_bytes)
    f = open("temp", 'w')
    f.write(key_str)
    """data = key_str.replace("-----BEGIN PUBLIC KEY-----", "")
    data = data.replace("-----END PUBLIC KEY-----", "")
    data = data.
    print(data)
    return data"""
    f.close()


if __name__ == '__main__':
    public_key, private_key = asymkey_gen()
    symkey, encrypted_symkey = symkey_gen(public_key)
    print(type(encrypted_symkey))

    """print("Clé symétrique : ", symkey)
    print("Clé symétrique cryptée : ", encrypted_symkey)
    print("Clé symétrique décryptée :", decrypt_asym(encrypted_symkey, private_key))

    print("Clé asymétrique :", public_key)"""

    msg = "Test sur un message plus long, parce qu'il faut que ça fonctionne même avec un plus long message"
    #print("Message : ", msg)
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_str = public_pem.decode("Utf8")
    print(type(public_str))
    print(type(public_str))
    public_pem2 =public_str.encode("utf8")
    public_key2 = load_pem_public_key(public_pem2, default_backend())
    token = encrypt_sym(msg, symkey)
    print(type(token))
    sym_crypt = encrypt_asym(symkey, public_key2)
    sym_decrypt = decrypt_asym(sym_crypt, private_key)
    print(sym_decrypt)
    print(symkey)


    print("Message encrypté : ", token)
    print("Message décrypté : ", decrypt_sym(token, symkey))