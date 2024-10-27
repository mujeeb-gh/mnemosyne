from flask import Flask, jsonify, render_template, Response
import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace
import logging
import base64
from flask import request

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Initialize the camera
cap = cv2.VideoCapture(0)

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

@app.route('/capture', methods=['POST'])
def capture():
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
                cv2.imwrite('../assets/centralized_face.png', face_img)
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

@app.route('/video')
def video():
    video_source = request.args.get('source', default=0)
    return Response(generate_frames(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)