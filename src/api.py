import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify, render_template, Response, request, session, url_for, redirect
from functools import wraps
from brisque import BRISQUE
from deepface import DeepFace
from datetime import datetime
from settings import ASSETS_DIR, VECTOR_DB_DIR
from utils import generate_frames
import cv2
import numpy as np
import logging
import base64
import chromadb
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize Chroma client and collection
chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
collection = chroma_client.get_or_create_collection(name="Face_collection")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.json
            metadata = {
                "name": data.get("name"),
                "email": data.get("email"),
                "program": data.get("program"),
                "year_of_study": data.get("year_of_study"),
                "date_of_birth": data.get("date_of_birth"),
                "phone_number": data.get("phone_number"),
                "created_on": datetime.now().isoformat()
            }
            matric_no = data.get("matric_no")

            # Upsert the metadata with the unique ID
            collection.add(
                embeddings=[],  # No embeddings for registration
                metadatas=[metadata],
                ids=[matric_no]
            )

            return jsonify({"message": "User registered successfully"})
        except Exception as e:
            logging.exception(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return render_template('register.html') 

@app.route('/face/capture', methods=['GET', 'POST'])
def capture_face():
    if request.method == 'POST':
        try:
            # Get the base64 image data from the request
            image_data = request.json.get('image')
            if not image_data:
                logging.exception("No image data received")
                return jsonify({"error": "No image data received"}), 400

            # Convert base64 to image
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Load the Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                logging.info(f"Face coordinates: {x}, {y}, {w}, {h}")

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
                    logging.error(f"Anti-spoofing error: {str(e)}")
                    return jsonify({"error": "Failed to perform anti-spoofing check"}), 400

                if spoof_confidence == False:
                    cv2.imwrite(ASSETS_DIR / f'spoofed_{uuid.uuid4()}.png', face_img)
                    logging.warning("Spoofed Image Detected, Use Real Face!!")
                    return jsonify({"message": "Spoofed Image Detected, Use Real Face!!"}), 400

                if quality < 45:
                    cv2.imwrite(ASSETS_DIR / f'centralized_face_{(uuid.uuid4())}.png', face_img)
                    logging.info("Image saved as centralized_face.png")
                    logging.info(f"Image Quality Score: {quality}")
                    logging.info(f"Anti-Spoofing Confidence: {spoof_confidence}")

                    return jsonify({
                        "message": "Image capture completed, saved as centralized_face.png.",
                        "quality": quality,
                        "anti_spoofing_confidence": spoof_confidence
                    }), 200
                else:
                    return jsonify({
                        "message": "Image quality too low",
                        "quality": quality,
                        "anti_spoofing_confidence": spoof_confidence
                    }), 400
            else:
                return jsonify({"error": "No face detected in image"}), 400

        except Exception as e:
            logging.exception(f"Unexpected error: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return render_template('capture.html')

@app.route('/video')
def video():
    video_source = request.args.get('source', default=0)
    return Response(generate_frames(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)