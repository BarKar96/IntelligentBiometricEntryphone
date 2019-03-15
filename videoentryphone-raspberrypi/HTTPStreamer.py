#import TCPServer
#import TCPClient
#import UDPListener
#import UDPSender
import queue
import io
import cv2
import picamera
import numpy as np
import logging
import socketserver
from threading import Condition
from http import server
from threading import Thread

PAGE="""\
<html>
<head>
</head>
<body>
<img src="stream.mjpg" width="360" height="640" />
</body>
</html>
"""

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

        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))

        cv2.putText(frame, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
            


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        data = np.fromstring(output.buffer.getvalue(), dtype=np.uint8)
                        # "Decode" the image from the array, preserving colour
                        image = cv2.imdecode(data, 1)
                        
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        recognizeFacesWithConfidence(gray,image);
                        
                        ret, qq = cv2.imencode('.jpg',image)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(qq))
                    self.end_headers()
                    self.wfile.write(qq)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

recognizer, faceCascade, id, names = initializeRecognizer()
output = StreamingOutput()

    

with picamera.PiCamera(resolution='360x640', framerate=30) as camera:
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()










