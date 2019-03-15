import pyaudio
import wave
from threading import Thread


chunk = 1024
wf = wave.open("beep.wav", 'rb')


global isRinging
isRinging = False

def stop_ringing_sound():
    global isRinging
    isRinging = False

def play_music():
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    global isRinging
    isRinging = True
    stream.start_stream()
    wf.rewind()
    data = wf.readframes(chunk)
    while len(data)>0:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
    

def play_ringing_sound_on_another_thread():
    Tp = Thread(target=play_music, args=())
    Tp.setDaemon(True)
    Tp.start()
    
##play_ringing_sound_on_another_thread()
##while(True):
##    pass


