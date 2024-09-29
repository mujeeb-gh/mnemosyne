import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace
from settings import DEFAULT_CAM
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def initialize_camera(cam_source):
    cap = cv2.VideoCapture(cam_source)
    if not cap.isOpened():
        logging.error("Camera failed to open.")
        return None
    return cap

def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to grab frame.")
        return None
    return frame

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    return faces

def adjust_face_coordinates(x, y, w, h):
    neck_extension = int(1.5 * h)
    new_h = h + neck_extension

    head_extension = int(0.8 * h)
    new_y = max(0, y - head_extension)

    width_extension = int(0.8 * w)
    new_x = max(0, x - width_extension // 2)
    new_w = w + width_extension

    return new_x, new_y, new_w, new_h

def check_image_quality(face_img):
    ndarray = np.asarray(face_img)
    obj = BRISQUE(url=False)
    quality = obj.score(img=ndarray)
    logging.info(f"Image Quality Score: {quality}")
    return quality

def save_image(face_img, path='assets/centralized_face.png'):
    cv2.imwrite(path, face_img)
    logging.info(f"Image saved as {path}")
    return path

def perform_anti_spoofing(img_path):
    face_objs = DeepFace.extract_faces(img_path=img_path, anti_spoofing=True)
    face = face_objs[0]
    return face["is_real"], face["antispoof_score"]

def capture_image():
    cap = initialize_camera(DEFAULT_CAM)
    if not cap:
        return {"error": "Could not open camera."}

    while True:
        frame = capture_frame(cap)
        if frame is None:
            return {"error": "Failed to grab frame."}

        faces = detect_faces(frame)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            logging.info(f"Face coordinates: {x}, {y}, {w}, {h}")

            new_x, new_y, new_w, new_h = adjust_face_coordinates(x, y, w, h)
            face_img = frame[new_y:new_y + new_h, new_x:new_x + new_w]

            quality = check_image_quality(face_img)
            if quality <= 50:
                img_path = save_image(face_img)
                is_real, spoof_confidence = perform_anti_spoofing(img_path)
                logging.info(f"Spoof Verification: {is_real}, Confidence: {spoof_confidence}")
                return {"message": "Image saved as centralized_face.png", "IS image real": is_real, "quality_score": spoof_confidence}
            else:
                return {"message": "Poor image quality, retake", "quality_score": quality}

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_image()