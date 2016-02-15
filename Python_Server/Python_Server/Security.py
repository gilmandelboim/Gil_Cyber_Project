#region ----------   ABOUT   -----------------------------
"""
##################################################################
# Created By: Michael Chernovilski                               #
# Date: 23/09/2014                                               #
# Name: Encryption & Decryption Script                           #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 64-bit                          #
# Python Tested Versions: 2.7 32-bit                             #
# Python Environment  : PyCharm                                  #
# pyCrypto Tested Versions: Python 2.7 32-bit                    #
##################################################################
"""
#endregion

# region--------------------------------------------IMPORTS-----------------------------------------
from Crypto.PublicKey import RSA

from Crypto.Random.random import getrandbits, randint
from Crypto import Random
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import pickle
from AES import *
import time


# endregion

# region-------------------------------------------CONSTANTS----------------------------------------
KEY_LENGTH = 1024
PORT = 6070
LEN_UNIT_BUF = 2048                                       # Min len of buffer for receive from server socket
MAX_ENCRYPTED_MSG_SIZE = 128
MAX_SOURCE_MSG_SIZE = 128
END_LINE = "\r\n"
# endregion

class Security:
    private_key = None

    # ----------------------------------------------------------
    def __init__(self):
        self.private_key = RSA.generate(KEY_LENGTH, Random.new().read)
        self.aes = AESCrypt()



    # region-----------------FUNCTIONS--------------------------
    # ----------------------------------------------------------
    def encrypt_sym_key(self, data, key):
        return key.encrypt(data)
    # ----------------------------------------------------------
    def decrypt_sym_key(self, encrypted, key):
        return key.decrypt(encrypted)
    # ----------------------------------------------------------

    def encrypt(self, data, public_key):
        pack_data = self.pack(data)
        if not public_key:
            public_key = self.private_key.publickey()
        return public_key.encrypt(pack_data, 32)[0]

    # ----------------------------------------------------------
    def decode(self, data, private_key):
        if not private_key:
            private_key = self.private_key
        decrypt_data = private_key.decrypt(data)

        return self.unpack(decrypt_data)

    # ----------------------------------------------------------
    def unpack(self, data):
        return pickle.loads(b64decode(data))

    # ----------------------------------------------------------
    def pack(self, data):
        return b64decode(pickle.dumps(data))

    #-----------------------------------------------------------------------------------------------
    #  Key Exchange
    #
    # Description: 
    #-----------------------------------------------------------------------------------------------
    def  key_exchange(self, client_socket):
        if self.private_key.can_encrypt():
             #--------------------  1 ------------------------------------------------------------------------
             # ------------  Send  server publicKey
             client_socket.send(pickle.dumps(self.private_key.publickey()) + END_LINE)
             time.sleep(0.5)
             # -----------  send  Base64 Hash of self.crypto.private_key.publickey()
             client_socket.send(b64encode(SHA256.new(pickle.dumps(self.private_key.publickey())).hexdigest()) + END_LINE)
             time.sleep(0.5)

             #--------------------  2 ------------------------------------------------------------------------
             # --------------  Wait client private key  --------------------------------------------------------
             # get Pickled private  key
             pickled_client_private_key = client_socket.recv(LEN_UNIT_BUF).split(END_LINE)[0]
             client_private_key = pickle.loads(pickled_client_private_key)

             # --------------  Wait client hash private key  ---------------------------------------------------------------------------
             # Hashing original  client private key
             calculated_hash_client_pickled_private_key = SHA256.new(pickle.dumps(client_private_key)).hexdigest()
             declared_hash_client_pickled_private_key = b64decode( client_socket.recv(LEN_UNIT_BUF).split(END_LINE)[0] )
             if calculated_hash_client_pickled_private_key != declared_hash_client_pickled_private_key:
                   print "Error : hash and original"
                   return

             client_private_key = RSA.importKey(client_private_key)

             ''' Due to a bug in pyCrypto, it is not possible to decrypt RSA messages that are longer than 128 byte.
                        To overcome this problem, the following code receives  the encrypted data in chunks of 128 byte.
                        We need to think how to tell the students about this behavior (another help message?)
                        And maybe we should implemented this approach in level 3 as well...
             '''

             #--------------------  3 ------------------------------------------------------------------------
             #  -------------- Receive from client in parts message
             #  -------------- encrypted by server public key info containing symmetric key and hash symmetric key encrypted by client public key
             pickled_client_key = ''
             pickled_encrypted_client_key = ''
             #   Recieve from client number of encrypted message parts
             msg_parts = client_socket.recv(LEN_UNIT_BUF).split(END_LINE)[0]
             for i in xrange(int(msg_parts)):
                    # Wait from client current part of encrypt client_key
                    part_pickled_encrypted_client_key = client_socket.recv(LEN_UNIT_BUF).split(END_LINE)[0]
                    pickled_encrypted_client_key += part_pickled_encrypted_client_key
                    # Decryption current part of encrypt client_key
                    part_encrypt_client_key = pickle.loads(part_pickled_encrypted_client_key)
                    part_pickled_client_key = self.private_key.decrypt(part_encrypt_client_key)
                    pickled_client_key += part_pickled_client_key
             items = pickled_client_key.split('#')
             client_sym_key_original = b64decode(items[0])
             print 'Client Sym Key Original :     ' + client_sym_key_original
             #--------   Extract Client Hash Sym Key
             client_encrypted_hash_sym_key = b64decode(items[1])
             client_encrypted_hash_sym_key = pickle.loads(client_encrypted_hash_sym_key)

             splitted_client_encrypted_hash_sym_key = [client_encrypted_hash_sym_key[i:i+MAX_ENCRYPTED_MSG_SIZE] for i in xrange(0, len(client_encrypted_hash_sym_key), MAX_ENCRYPTED_MSG_SIZE)]
             msg_parts = len(splitted_client_encrypted_hash_sym_key)
             client_hash_sym_key = ''
             for i in xrange(int(msg_parts)):
                    # Decryption current part of encrypt client_key
                    part_client_encrypted_hash_sym_key = client_private_key.decrypt(splitted_client_encrypted_hash_sym_key[i])
                    client_hash_sym_key += part_client_encrypted_hash_sym_key
             print 'Client Hash Sym Key  :     ' + client_hash_sym_key
             calculated_client_sym_key_original = SHA256.new(client_sym_key_original).hexdigest()
             if calculated_client_sym_key_original != client_hash_sym_key:
                   print "Error : hash and original"
             return client_sym_key_original

    # endregion
