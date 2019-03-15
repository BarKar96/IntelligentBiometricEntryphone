import cv2
import os

cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video width
cam.set(4, 480) # set video height

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# For each person, enter one numeric face id
face_name = input('\n enter user name and press <return> ==>  ')
face_id = 10
if os.stat("people.txt").st_size == 0:
    with open('people.txt',"w+") as myfile:
        face_id = 1
        myfile.write(str(face_id) + " " + face_name + "\n")
        myfile.close()
else:
    last =""
    with open('people.txt', "r") as myfile:
        for line in myfile:
            last = line
    with open('people.txt', "a") as myfile:
        word = last.split(' ',1)
        print(word[0])
        face_id = int(word[0]) + 1
        myfile.write(str(face_id) + " " + face_name + "\n")
        myfile.close()


print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while(True):

    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

    cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif count >= 30: # Take 30 face sample and stop video
         break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()


