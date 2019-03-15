import pyaudio
import socket
from threading import Thread

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
addressRPi = ''
frames = []
global speakersActivated
speakersActivated = False

audio = pyaudio.PyAudio()


def captureUDPAudioFrames():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind((addressRPi, 7000))
    print("UDPListener    capturingUDPAudioFrames")
    while speakersActivated:
        data, addr = udp.recvfrom(CHUNK)
        frames.append(data)
    udp.close()


def playAudio():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        output=True, frames_per_buffer=CHUNK)
    print("UDPListener    playingAudio")
    while speakersActivated:
        if len(frames) > 0:
            stream.write(frames.pop(0))
    print("UDPListener    closing socket")
    stream.close()

def startUDPListener():
    frames.clear()
    Ts = Thread(target=captureUDPAudioFrames, args=())
    Tp = Thread(target=playAudio, args=())
    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Ts.start()
    Tp.start()
#    Ts.join()
#    Tp.join()




#print('hello there from UDPListener')










