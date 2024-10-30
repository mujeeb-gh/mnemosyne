import tensorflow as tf
from flask import Flask, jsonify
import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function for capturing image and quality check
def capture_image():
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Camera failed to open.")
        return {"error": "Could not open camera."}

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame.")
            return {"error": "Failed to grab frame."}
        
        # Show the live feed
        cv2.imshow('Video Feed', frame)
        
        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        # If faces are detected
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            print("Face coordinates:", x, y, w, h)

            # Add neck, head, and width adjustments
            neck_extension = int(1.5 * h)
            new_h = h + neck_extension

            head_extension = int(0.8 * h)
            new_y = max(0, y - head_extension)

            width_extension = int(0.8 * w)
            new_x = max(0, x - width_extension // 2)
            new_w = w + width_extension
            
            # Extract the face image with the adjustments
            face_img = frame[new_y:new_y + new_h, new_x:new_x + new_w]

            # Convert the face image to a NumPy array
            ndarray = np.asarray(face_img)

            # Run the BRISQUE quality check
            obj = BRISQUE(url=False)
            quality = obj.score(img=ndarray)

            # Perform anti-spoofing using DeepFace
            try:
                face_objs = DeepFace.extract_faces(img_path=ndarray, anti_spoofing=True)
                face = face_objs[0]
                spoof_confidence = face["is_real"]

            except Exception as e:
                print(f"Anti-spoofing error: {str(e)}")
                continue  # Skip this iteration if there's an issue with detection
            if spoof_confidence == False:
                cv2.imwrite('assets/spoofed.png', face_img)
                print("Spoofed Image Detected, Use Real Face!!")
                break
            if quality < 40:
                cv2.imwrite('assets/centralized_face.png', face_img)
                print("Image saved as centralized_face.png")
                print(f"Image Quality Score: {quality}")
                print(f"Anti-Spoofing Confidence: {spoof_confidence}")
                break  # Exit the loop if both criteria are satisfied
            else:
                print(f"Quality: {quality}, Spoof Confidence: {spoof_confidence}")
        
        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_image()
