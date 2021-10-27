import cv2, os
import numpy as np
from os import listdir
from os.path import isfile, join
from vicks import crud

face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

try:
    os.mkdir('testing')
except Exception as e:
    print(e)
    pass

def scan():
    def face_extractor(img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        if faces is ():
            return None

        for (x,y,w,h) in faces:
            cropped_face = img[y:y+h, x:x+w]

        return cropped_face

    cap = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cap.read()
        if face_extractor(frame) is not None:
            count += 1
            face = cv2.resize(face_extractor(frame), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            file_name_path = 'testing/' + str(count) + '.jpg'
            cv2.imwrite(file_name_path, face)

            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Face Cropper', face)

        else:
            print("Face not found")
            pass

        if cv2.waitKey(1) == 13 or count == 100:
            break


    cap.release()
    cv2.destroyAllWindows()
    print("Collecting Samples Complete")

# ============================================

def training():
    print(cv2.__version__)

    data_path = 'testing/'
    onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
    Training_Data, Labels = [], []

    for i, files in enumerate(onlyfiles):
        image_path = data_path + onlyfiles[i]
        images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        Training_Data.append(np.asarray(images, dtype=np.uint8))
        Labels.append(i)
    #
    Labels = np.asarray(Labels, dtype=np.int32)
    model=cv2.face_LBPHFaceRecognizer.create()

    model.train(np.asarray(Training_Data), np.asarray(Labels))
    return model

# ===========================================

def testing(model):
    def face_detector(img, size=0.5):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        if faces is ():
            return img, []

        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),2)
            roi = img[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))
        return img, roi


    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        image, face = face_detector(frame)

        try:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            results = model.predict(face)
            print(results)

            if results[1] < 500:
                confidence = int( 100 * (1 - (results[1])/400) )
                # print(confidence)
                display_string = str(confidence) + '% Confident'

            cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255,120,150), 2)

            if confidence > 88:
                # print(confidence)
                cv2.putText(image, "Criminal Detected", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                cv2.imshow('Face Recognition', image )

                obj1 = crud.vicks('@Hey_Vicks', link = 'https://home-automation-336c0-default-rtdb.firebaseio.com/')
                obj1.push(data = 1, child = 'A/B/C/Switch')

            else:
                print(confidence)
                cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
                cv2.imshow('Face Recognition', image )

        except Exception as e:
            # print(e)
            cv2.putText(image, "Face Not Found", (220, 120) , cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
            cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
            cv2.imshow('Face Recognition', image )
            pass

        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()

# scan()
# testing(training())
