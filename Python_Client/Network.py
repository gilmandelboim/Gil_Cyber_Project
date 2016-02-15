#region ----------   ABOUT   -----------------------------
"""
##################################################################
# Created By:  Michael Chernovilski                              #
# Date: 20/09/2014                                               #
# Name: Server  between GUI and clients                          #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
# pyCrypto Tested Versions: Python 2.7 32-bit                    #
##################################################################
"""
#endregion

#region ----------   IMPORTS   -----------------------------
import threading
import os
import socket
import time
from Security import *
#endregion

#region ----------   C O N S T A N T S  ------------------------------------------------------
PROT_START = "Hello"                                      # Initialization keyword of Protocol Establishment
LEN_UNIT_BUF = 2048                                       # Min len of buffer for receive from server socket
ERROR_SOCKET = "Socket_Error"                             # Error message If you happened socket error
ERROR_EXCEPT = "Exception"                                # Error message If you happened exception
MAX_ENCRYPTED_MSG_SIZE = 128
MAX_SOURCE_MSG_SIZE = 128
END_LINE = "\r\n"                                         # End of line
SERVER_ABORT = "Aborting the server..."
#endregion

#region  -----  SessionWithClient C L A S S  -----#region ----------   ABOUT   -----------------------------
"""
##################################################################
# Created By:  Michael Chernovilski                              #
# Date: 20/09/2014                                               #
# Name: Server  between GUI and clients                          #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
# pyCrypto Tested Versions: Python 2.7 32-bit                    #
##################################################################
"""
#endregion

#region ----------   IMPORTS   -----------------------------
import os
import socket
import time
from Security import *
from Database import *

#endregion

#region ----------   C O N S T A N T S  ------------------------------------------------------
PROT_START = "Hello"                                      # Initialization keyword of Protocol Establishment
LEN_UNIT_BUF = 2048                                       # Min len of buffer for receive from server socket
ERROR_SOCKET = "Socket_Error"                             # Error message If you happened socket error
ERROR_EXCEPT = "Exception"                                # Error message If you happened exception
MAX_ENCRYPTED_MSG_SIZE = 128
MAX_SOURCE_MSG_SIZE = 128
END_LINE = "\r\n"                                         # End of line
SERVER_ABORT = "Aborting the server..."
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8106
#endregion

#region  -----  SessionWithClient C L A S S  -----
class NetWorkClient:
    def __init__(self):
        self.security = Security()
        self.sym_key =None
        self.sock = socket.socket()
        self.AES= AESCrypt()
        self.Database= Database()

    def start(self):
        self.sock.connect((SERVER_ADDRESS, SERVER_PORT))

    def recv_buf(self):
        #content=""
        #while True:
        #    data = self.clientSock.recv(LEN_UNIT_BUF)
        #    if not data:  break
        #    content += data
        #print content
        #return content.split(END_LINE)[0]
        return self.sock.recv(LEN_UNIT_BUF).split(END_LINE)[0]

    def verify_hello(self, data):
        if len(data):
            # Verify Hello at beginning of communication
            if not (data == PROT_START ):
                self.sock.send(ERROR_SOCKET + END_LINE + "Error in protocol establishment ( 'Hello' )" + END_LINE)
                time.sleep(0.5)
                self.sock.close()
                return False
            return True
        return False

    def send(self, data):
        data = self.AES.encryptAES(self.sym_key, data)
        self.sock.send(data)

    def recv(self):
        encrypted_data = self.sock.recv(LEN_UNIT_BUF)
        data = self.AES.decryptAES(self.sym_key, encrypted_data)
        return data

    def run(self):
        connect= False
        while connect== False:
            try:
                self.start()
                self.sock.send(PROT_START)
                data = self.recv_buf()
                if not self.verify_hello(data):
                    return
                self.sym_key = self.security.key_exchange_client(self.sock)
                print self.sym_key
                connect=True
                while data!="get info":
                    data = self.recv()
                    print data
                    if data=="get info":
                        #send all information about client
                        dict=self.Database.get_dict_from_table("WORDS")
                        self.send(self.Database.get_most_used_words(dict))

            except:
                print "still cant find server"
                time.sleep(5)





