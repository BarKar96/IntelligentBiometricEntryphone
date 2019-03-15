import socket
import queue
from threading import Thread

addressRPi = ''


global q
q = queue.Queue()

def startTCPListener():
    Ts = Thread(target=captureTCPFrames, args=())
    Ts.setDaemon(True)
    Ts.start()
    


def captureTCPFrames():
    print("TCPServer    captureTCPFrames")
    TCP_PORT = 9000
    BUFFER_SIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((addressRPi, TCP_PORT))
    s.listen(10)


    print('TCPServer    working on ' + str(addressRPi) + " port: " + str(TCP_PORT))
    while 1:
        #print("waiting for client")
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        #print("received data:" + data.decode('utf-8'))
        q.put(data.decode('utf-8'))
        #print(q.get(), end=' ')
    conn.close()

def clearQueue():
    with q.mutex:
        q.queue.clear()
