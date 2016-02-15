#region ----------   ABOUT   -----------------------------
"""
##################################################################
# Created By:                                          #
# Date: 21/01/2016                                               #
# Name: Server  between GUI and clients                          #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
#endregion

#region ----------   IMPORTS   -----------------------------
import threading,socket, sys, os
from SessionWithClient import *
import struct

#endregion


#region -----  CONSTANTS  -----
# For every client to been thread
THREAD_LIMIT = 50
GUI_PORT = 9669
SERVER_ABORT = "Aborting the server..."
#endregion

#region ----------   CLASSES   -----------------------------
#region -----  PythonServer CLASS  -----
class  PythonServer(threading.Thread):   
    # -----  DATA  -----
    listenerSock = None
    # Dictionary for client connctions : Key - ip  Value - SessionWithClient
    open_clients = {}       
 
    # constructor 
    def __init__(self, listenerPort):
       # self.gui = gui
        self.listenerPort = listenerPort
        threading.Thread.__init__(self)
                
    # the main thread function
    def run(self):
        """
        import time
        import struct

        f = open(r'\\.\pipe\NPtest1', 'r+b', 0)
        while True:
          s = 'Message[{0}]'.format(i)
          i += 1

          f.write(struct.pack('I', len(s)) + s)   # Write str length and str
          f.seek(0)                               # EDIT: This is also necessary
          print 'Wrote:', s

          n = struct.unpack('I', f.read(4))[0]    # Read str length
          s = f.read(n)                           # Read str
          f.seek(0)                               # Important!!!
          print 'Read:', s

          time.sleep(2)
          """

        #self.gui.guiSock.send("Server running...Waiting for a connection...#")   # to GUI
        try:
            # Listener socket
            listenerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print self.listenerPort
            listenerSock.bind(("0.0.0.0", self.listenerPort))
            listenerSock.listen(5)
           # self.gui.guiSock.send("Listening to clients...#")   # to GUI
            open_clients_string=""
            f = open(r'\\.\pipe\NPtest1', 'r+b', 0)
            while True:

                print self.open_clients
                for key in self.open_clients:
                    open_clients_string=";"+key
                print open_clients_string
                open_clients_string=open_clients_string[1:]
                f.write(struct.pack('I', len( open_clients_string)) + open_clients_string)
                f.seek(0)

                clientSock, addr = listenerSock.accept()
                # Thread creating loop
                while True:
                    if threading.activeCount() < THREAD_LIMIT:
                        clientIP = addr[0]  # key - IP client
                        print clientIP
                        # Check if client connected in pass
                        if clientIP in self.open_clients:
                            pass
                            # Callback Connection by IP clientIP
                           # self.gui.guiSock.send("Callback Connection by " +  clientIP + " clientIP#")   # to GUI
                        else:
                            pass

                            # First Connection by IP  clientIP

                            sessionWithClient = SessionWithClient(self, clientSock, addr, None)
                            self.open_clients[clientIP] = sessionWithClient
                            sessionWithClient.start()

                        break
        except socket.error , er_msg:
            error_code = er_msg[0]
            if error_code == 10048:
                #self.gui.guiSock.send("Port " + str(self.listenerPort) + " is busy#")   # to GUI
                pass
            else:
                #self.gui.guiSock.send(str(er_msg) + "#")   # to GUI
                pass
        except Exception as er_msg:
           #self.gui.guiSock.send(str(er_msg) + "#")   # to GUI
            pass

#endregion

