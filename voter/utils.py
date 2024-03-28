import cv2
import numpy as np
from .models import User

# Load the pre-trained face recognition model
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load the face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def train_face_recognizer():
    # Retrieve user data from the database
    users = User.objects.all()

    # Prepare data for face recognition
    faces = []
    labels = []
    for user in users:
        # Read user's profile image
        img = cv2.imread(user.profile_image.path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces_rect = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces_rect:
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            faces.append(face_roi)
            labels.append(user.id)

    # Train the face recognizer
    face_recognizer.train(faces, np.array(labels))

def recognize_faces(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces_rect = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    recognized_faces = []

    for (x, y, w, h) in faces_rect:
        # Extract face region
        face_roi = gray[y:y+h, x:x+w]

        # Recognize the face
        label, confidence = face_recognizer.predict(face_roi)

        # If the confidence is below a certain threshold, consider it a match
        if confidence < 100:
            # Retrieve user information based on the label
            user = User.objects.get(id=label)
            recognized_faces.append({"user": user, "confidence": confidence})

    return recognized_faces
