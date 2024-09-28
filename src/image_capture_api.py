import tensorflow as tf
from flask import Flask, jsonify, request
import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace

# Initialize Flask app
app = Flask(__name__)

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function for capturing image and quality check
def capture_image():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {"error": "Could not open camera."}

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            return {"error": "Failed to grab frame."}

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]

            # Add neck, head, and width adjustments
            neck_extension = int(1.5 * h)
            new_h = h + neck_extension

            head_extension = int(0.8 * h)
            new_y = max(0, y - head_extension)

            width_extension = int(0.8 * w)
            new_x = max(0, x - width_extension // 2)
            new_w = w + width_extension

            face_img = frame[new_y:new_y + new_h, new_x:new_x + new_w]

            # Quality check using BRISQUE
            ndarray = np.asarray(face_img)
            obj = BRISQUE(url=False)
            quality = obj.score(img=ndarray)

            if quality <= 40:
                # Save the face image
                cv2.imwrite('assets\centralized_face.png', face_img)

                # Perform anti-spoofing
                img_path = 'assets\centralized_face.png'
                face_objs = DeepFace.extract_faces(img_path=img_path, anti_spoofing=True)

                face = face_objs[0]
                Spoof_verification = face["is_real"]
                spoof_confidence = face["antispoof_score"]

                # Check if the face is a spoof or real
                if not Spoof_verification:
                    return {
                        "message": "Spoof detected. Please use a real face image.",
                        "anti_spoofing_score": spoof_confidence,
                        "quality_score": quality
                    }
                else:
                    return {
                        "message": "Image saved as centralized_face.png",
                        "is_image_real": Spoof_verification,
                        "anti_spoofing_score": spoof_confidence,
                        "quality_score": quality
                    }
            else:
                return {"message": "Poor image quality, retake", "quality_score": quality}

    cap.release()
    cv2.destroyAllWindows()

# Define API route for image capture
@app.route('/capture', methods=['GET'])
def capture_route():
    result = capture_image()
    return jsonify(result)

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
