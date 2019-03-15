import socket
import time
from threading import Thread




addressAndroid = ''
TCP_PORT = 9000
BUFFER_SIZE = 1024

def sendMessage(message):
    print("poczatek")
    MESSAGE = message
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addressAndroid, TCP_PORT))
    print ("TCPClient: " + message)
    s.send(MESSAGE.encode('utf-8'))
    print("koniec")
    s.close()


def startTCPClient(message):
    Ts = Thread(target=sendMessage, args=(message,))
    Ts.setDaemon(True)
    Ts.start()
    #Ts.join()

