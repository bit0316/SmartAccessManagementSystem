import os
import cv2
import time
import numpy as np
from PIL import Image
import user_data

# Variable
path = 'Dataset/User'
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('Trainer/trainer.yml')
detector = cv2.CascadeClassifier(cascadePath)
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

# Face dataset (capture face to model training)
def face_dataset(face_id):
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height
    
    print("[INFO] Initializing face capture. Look the camera and wait ...\n")
    count = 0 # Initialize individual sampling face count
    while(True):
        ret, img = cam.read()
        img = cv2.flip(img, -1)
        cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        # Save the captured image into the datasets folder
        for (x,y,w,h) in faces:
            count += 1
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            cv2.imwrite(path + "/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imshow('image', img)

        # Press 'ESC' for exiting video
        k = cv2.waitKey(100) & 0xff
        if k == 27:         break
        # Take 50 face sample and stop video
        elif count >= 50:   break

    # Do a bit of cleanup
    print("[INFO] Exiting Program and cleanup stuff\n")
    cam.release()
    cv2.destroyAllWindows()

# Function to get the images and label data
def get_images_and_labels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]     
    faceSamples = []
    ids = []
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
    return faceSamples, ids

# Face training
def face_training():
    print ("[INFO] Training faces. It will take a few seconds. Wait ...\n")
    faces, ids = get_images_and_labels(path)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write('Trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

    # Print the numer of faces trained and end program
    print("[INFO] {0} Faces trained. Exiting Program\n".format(len(np.unique(ids))))

# Face recognition (doorlock)
def face_recognition(doorlock):
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    # Time measurement
    start_time = time.time()
    unrecognizable_time = 0
    unrecognized_time = 0
    isError = False

    # Start face recognition
    while doorlock.isLock:
        ret, img =cam.read()
        img = cv2.flip(img, -1) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale( 
            gray, scaleFactor = 1.2, minNeighbors = 5,minSize = (int(minW), int(minH)),
        )

        # Unrecognizable face
        if len(faces) == 0:
            unrecognizable_time = time.time() - start_time
            if unrecognizable_time > 10:
                print("Unrecognizable!! Please try again...\n")
                doorlock.incorrect("Unrecognizable")
                break
        # Recognizable face
        else:
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

                # Check if confidence is less than 100 and greater than 60
                if (60 < (100 - confidence) < 100):
                    user_info = user_data.search_user_info(id)
                    if user_info:
                        user_data.print_user_info(id)
                        name = user_info["Name"]
                        confidence = "  {0}%".format(round(100 - confidence))
                        doorlock.open(name)
                        break
                else:
                    name = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))
                    unrecognized_time = time.time() - start_time
                    if unrecognized_time > 10:
                        print("No matching information")
                        doorlock.incorrect("Unrecognized")
                        isError = True
                        break
            
                cv2.putText(img, str(name), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
        cv2.imshow('camera', img) 
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:                     break
        if doorlock.isLock == False:    break
        if isError == True:             break

    # Do a bit of cleanup
    print("[INFO] Exiting Program and cleanup stuff\n")
    cam.release()
    cv2.destroyAllWindows()

# LCD.py -> call(server, face, doorlock)
def guest_face():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # set Width
    cap.set(4, 480)  # set Height

    ret, frame = cap.read()
    frame = cv2.flip(frame, -1)  # Flip camera vertically
    cv2.imwrite("Dataset/Guest/Guest.jpg", frame)

    cap.release()
    cv2.destroyAllWindows()
