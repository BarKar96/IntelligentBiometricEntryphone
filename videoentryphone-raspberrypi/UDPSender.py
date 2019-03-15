import pyaudio
import socket
from threading import Thread

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
addressAndroid = ''
frames = []
global microphoneActivated
microphoneActivated = False

audio = pyaudio.PyAudio()


def sendUDPAudioFrames():
    print("UDPSender    sendingUDPAudioFrames")
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while microphoneActivated:
        if len(frames) > 0:
            udp.sendto(frames.pop(0), (addressAndroid, 7000))
    print("UDPSender    closing socket")
    udp.close()


def recordAudio():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=int(CHUNK*2))
    print("UDPSender    recordingAudio")
    while microphoneActivated:
        frames.append(stream.read(int(CHUNK/2),exception_on_overflow = False))
    stream.close()

def startUDPSender():
    frames = []
    Tr = Thread(target=recordAudio, args=())
    Ts = Thread(target=sendUDPAudioFrames, args=())
    Tr.setDaemon(True)
    Ts.setDaemon(True)
    Tr.start()
    Ts.start()
#    Tr.join()
#    Ts.join()


#print('hello there from UDPSender')




