import LedBlinker
import CustomTimer
import KeypadManager
import TCPServer
import TCPClient
import UDPListener
import UDPSender
import Diffie_Hellman
from AESCipher import AESCipher
import SoundPlayer
import queue
import io
import cv2
import picamera
import numpy as np
import logging
import socketserver
import time
import sys
from threading import Condition
from threading import Timer
from http import server
from threading import Thread, Event
from subprocess import Popen, PIPE

addressRPi = "192.168.1.15"
addressAndroid = "192.168.1.11"

def setIPAddresses():
    addressRPi = str(sys.argv[1])
    addressAndroid = str(sys.argv[2])
    TCPServer.addressRPi = addressRPi
    TCPClient.addressAndroid = addressAndroid
    UDPSender.addressAndroid = addressAndroid
    UDPListener.addressRPi = addressRPi
setIPAddresses()

def letIn():
    CustomTimer.q.put("IDENTITY_MATCHED")
    LedBlinker.blink("GREEN")
    print("identity matched")

def initializeRecognizer():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    id = 0
    names = ['None']
    with open('people.txt', "r") as myfile:
        for line in myfile:
            word = line.split(' ')
            word = word[1]
            name = word[:-1]
            names.append(name)

    return recognizer, faceCascade, id, names


def initializeCamera():

    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    return cam, minW, minH

def recognizeFacesWithConfidence(gray,frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(0.1*360), int(0.1*640)),
    )

    for (x, y, w, h) in faces:

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        confidence = round(100 - confidence)
        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100 and confidence > 40):
            id = names[id]
            confidence = "  {0}%".format(confidence)
            letIn()
        else:
            id = "unknown"
            confidence = "  {0}%".format(confidence)

        cv2.putText(frame, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

def recognizeFaceModule():
    CustomTimer.startTimer(10)
    global phoneStatus
    while CustomTimer.q.empty():
        ret, img = cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        recognizeFacesWithConfidence(gray,img)
        cv2.imshow('camera',img)
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
    if CustomTimer.q.get() == "STOP":
        LedBlinker.blink("RED")
    print("\n [INFO] Exiting Program and cleanup stuff")
    
    cam.release()
    cv2.destroyAllWindows()
    KeypadManager.clearQueue()
    phoneStatus = "FREE"

  
def startCall():
    processHTTPStreaming = Popen(['python3', 'HTTPStreamer.py'], stdout=PIPE, stderr=PIPE)
    time.sleep(4)
    messageToSend = aesCipher.encrypt("CALL")
    TCPClient.startTCPClient(messageToSend)
    print("wysylam start call")
    UDPSender.microphoneActivated = True;
    UDPListener.speakersActivated = True;
    UDPListener.startUDPListener()
    return processHTTPStreaming

def endNotAnsweredCall():
    print("endNotAnsweredCall")
    messageToSend = aesCipher.encrypt("CANCEL")
    TCPClient.startTCPClient(messageToSend)
    UDPSender.microphoneActivated = False;
    UDPListener.speakersActivated = False;
    processHTTPStreaming.kill()

def ringingTimeout():
    global phoneStatus
    print("ringing Timeout - stopper_message: " + stopper_message)
    
    if stopper_message == "CALL_ANSWERED":
        phoneStatus = "BUSY"
                
    if stopper_message == "STOP_RINGING":
        phoneStatus = "FREE"
        endNotAnsweredCall()
            
           




processHTTPStreaming = None
recognizer, faceCascade, id, names = initializeRecognizer()
cam, minW, minH = None, None, None

TCPServer.startTCPListener()

KeypadManager.keypadActivated = True
KeypadManager.f()



stopper_message = ""
stopper = Event()
stopper.clear()
clientConnected = False

global phoneStatus
phoneStatus = "FREE"

aesCipher = AESCipher()





while True:
    
    while not KeypadManager.q.empty():
        messageFromKeypad = KeypadManager.q.get()
        if messageFromKeypad == "A":
            if phoneStatus == "FREE":
                SoundPlayer.play_ringing_sound_on_another_thread()
                if clientConnected == True:
                    phoneStatus = "BUSY"
                    print("MAIN KEYBOARD: A")
                    processHTTPStreaming = startCall()
                    stopper_message = "STOP_RINGING"
                    t = Timer(30.0, ringingTimeout)
                    t.start() 

            else:
                print(phoneStatus)
             
            
        if messageFromKeypad == "B":
            if phoneStatus == "FREE":
                SoundPlayer.play_ringing_sound_on_another_thread()
                phoneStatus = "BUSY"
                print("MAIN KEYBOARD: B")
                cam, minW, minH = initializeCamera()
                recognizeFaceModule()
                
    
    while not TCPServer.q.empty():
        message = TCPServer.q.get()
        print ("przychodzi wiadomosc "+ message)
        
        if message != "HI" and message[:2] != "DH":
            
            message = aesCipher.decrypt(message)
            
            
            
        if message == "OK":
            
            phoneStatus = "BUSY"
            print("MAIN TCP: OK")
            stopper_message = "CALL_ANSWERED"
            print("MAIN TCP: zmieniono na CALLAnswered")
            processHTTPStreaming.kill()
            UDPSender.startUDPSender()
        
              
        if message == "BYE":
            print("MAIN TCP: BYE")
            UDPSender.microphoneActivated = False;
            UDPListener.speakersActivated = False;
            LedBlinker.blink("RED")
            KeypadManager.clearQueue()
            phoneStatus = "FREE"
        
        if message == "LETIN":
            print("MAIN TCP: LETIN")
            UDPSender.microphoneActivated = False;
            UDPListener.speakersActivated = False;
            LedBlinker.blink("GREEN")
            KeypadManager.clearQueue()
            phoneStatus = "FREE"
            
        if message == "HI":
            print("MAIN TCP: HI")
            Diffie_Hellman.negotiateDHKeys()
        
        if message[:2] == "DH":
            
            print("MAIN TCP: " + message)
            sharedSecret = Diffie_Hellman.calculateSharedSecret(message[3:])
            print("sharedSecret is: " + str(sharedSecret))
            aesCipher.setKey(str(sharedSecret))
            clientConnected = True
            
            

print('koniec programu')






