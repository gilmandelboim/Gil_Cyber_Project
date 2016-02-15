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
import socket


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
        self.key = Random.new().read(int(16))
        self.aes=AESCrypt()

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
    def key_exchange(self, client_socket):
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


    def key_exchange_client(self,socket):
        #--------------------  1 ------------------------------------------------------------------------
        # --------------  Wait server Public_Key --------------------------------------------------------
        # get Pickled public key
        pickled_server_public_key = socket.recv(LEN_UNIT_BUF).split(END_LINE)[0]
        server_public_key = pickle.loads(pickled_server_public_key)
        # --------------  Wait server hash Public_Key ---------------------------------------------------------------------------
        # Hashing original Public_Key
        calculated_hash_server_pickled_public_key = SHA256.new(pickle.dumps(server_public_key)).hexdigest()
        declared_hash_server_pickled_public_key = b64decode(socket.recv(LEN_UNIT_BUF).split(END_LINE)[0] )
        if calculated_hash_server_pickled_public_key != declared_hash_server_pickled_public_key:
                    return "Not Magic"

        #--------------------  2 ------------------------------------------------------------------------
        # ------------  Send  client private key
        socket.send(pickle.dumps(self.private_key.exportKey()) + END_LINE)
        time.sleep(0.5)
        # -----------  send  Base64 Hash of self.crypto.private_key
        socket.send( b64encode(SHA256.new(pickle.dumps(self.private_key.exportKey())).hexdigest()) + END_LINE)
        time.sleep(0.5)

        #--------------------  3 ------------------------------------------------------------------------
        # -------------- Send  encrypted by server public key info containing symmetric key and hash symmetric key encrypted by client public key ---------------------
        if self.private_key.can_encrypt():
            hash_sym_key = SHA256.new(self.key).hexdigest()
            print str(hash_sym_key)
            pickle_encrypt_hash_sym_key = pickle.dumps(self.private_key.publickey().encrypt(hash_sym_key, 32))
            message = b64encode(self.key) + "#" + b64encode( pickle_encrypt_hash_sym_key )
            print message
            splitted_pickled_message = [message[i:i+MAX_ENCRYPTED_MSG_SIZE] for i in xrange(0, len(message), MAX_ENCRYPTED_MSG_SIZE)]
            #   Sending to server number of encrypted message parts
            socket.send(str(len(splitted_pickled_message)) + END_LINE)
            pickled_encrypted_message = ''
            for part in splitted_pickled_message:
                   part_encrypted_pickled_message = server_public_key.encrypt(part, 32)
                   pickled_part_encrypted_pickled_message = pickle.dumps(part_encrypted_pickled_message)
                   socket.send(pickled_part_encrypted_pickled_message + END_LINE)
                   pickled_encrypted_message += pickled_part_encrypted_pickled_message
                   time.sleep(0.5)
        return self.key


    # endregion
