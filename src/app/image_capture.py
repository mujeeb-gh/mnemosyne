from flask import Flask, jsonify, Response
import cv2
import numpy as np
from brisque import BRISQUE
from PIL import Image

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

        # If faces were detected, capture the first one and check quality
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_img = frame[y:y+h, x:x+w]
            ndarray = np.asarray(face_img)
            obj = BRISQUE(url=False)
            quality = obj.score(img=ndarray)
            if quality <= 30:
                cv2.imwrite('centralized_face.png', face_img)
                return {"message": "Image saved as centralized_face.png", "quality_score": quality}
            else:
                return {"message": "Poor image quality, retake", "quality_score": quality}

        # Optionally, you can display the frame for debugging purposes
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/capture', methods=['GET'])
def capture():
    result = capture_image()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
