from flask import Flask, jsonify, render_template, Response, request
import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace
import logging
import base64
import chromadb
from face_index import get_face_embedding
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize Chroma client and collection
chroma_client = chromadb.PersistentClient(path='vector_db')
collection = chroma_client.get_or_create_collection(name="Face_collection")

def generate_frames(video_source=0):
    if isinstance(video_source, str):
        cap = cv2.VideoCapture(video_source)
    else:
        cap = cv2.VideoCapture(int(video_source))
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        metadata = {
            "name": data.get("name"),
            "email": data.get("email"),
            "program": data.get("program"),
            "year_of_study": data.get("year_of_study"),
            "date_of_birth": data.get("date_of_birth"),
            "phone_number": data.get("phone_number"),
            "created_on": data.get("created_on")
        }
        matric_no = data.get("matric_no")  # Use the matric number from the request

        # Upsert the metadata with the unique ID
        collection.add(
            embeddings=[],  # No embeddings for registration
            metadatas=[metadata],
            ids=[matric_no]
        )

        return jsonify({"message": "User registered successfully"}), 200
    except Exception as e:
        logging.exception(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/face/capture', methods=['POST'])
def capture_face():
    try:
        # Get the base64 image data from the request
        image_data = request.json.get('image')
        if not image_data:
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
                cv2.imwrite('assets/spoofed.png', face_img)
                logging.warning("Spoofed Image Detected, Use Real Face!!")
                return jsonify({"message": "Spoofed Image Detected, Use Real Face!!"}), 400

            if quality < 45:
                cv2.imwrite('assets/centralized_face.png', face_img)
                logging.info("Image saved as centralized_face.png")
                logging.info(f"Image Quality Score: {quality}")
                logging.info(f"Anti-Spoofing Confidence: {spoof_confidence}")

                # Get face embedding
                face_embedding = get_face_embedding('assets/centralized_face.png', model_name='VGG-Face')

                # Generate a unique ID for each entry
                matric_no = '20/sci01/042'  # Replace with actual matric numbers or identifiers if unique per student

                # Define metadata
                metadata = {
                    "name": "Olamide Balogun",
                    "email": "olamide@lendsqr.com",
                    "program": "Computer Science",
                    "year_of_study": 4,
                    "date_of_birth": "2005-05-22",
                    "phone_number": "+2348126166902",
                    "timestamp": datetime.now().isoformat()  # Optional timestamp
                }

                # Upsert the face embedding and metadata with the unique ID
                collection.add(
                    embeddings=[face_embedding],
                    metadatas=[metadata],
                    ids=[matric_no]
                )

                # Verify the latest entry
                logging.info("Last entry metadata: %s", collection.get(ids=[matric_no]))

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

@app.route('/video')
def video():
    video_source = request.args.get('source', default=0)
    return Response(generate_frames(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)