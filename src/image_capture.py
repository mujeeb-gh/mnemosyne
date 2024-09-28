import cv2
import numpy as np
from brisque import BRISQUE
from deepface import DeepFace
from settings import DEFAULT_CAM, IP_WEBCAM_IP

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function for capturing image and quality check
def capture_image():
    # Initialize the camera with the IP address of your phone's camera stream
    cap = cv2.VideoCapture(DEFAULT_CAM)
    
    if not cap.isOpened():
        print("Camera failed to open.")
        return {"error": "Could not open camera."}

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame.")
            return {"error": "Failed to grab frame."}

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))


        # If faces were detected, capture the first one, check liveliness, and quality
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
            
            face_img = frame[new_y:new_y + new_h, new_x:new_x + new_w]

            ndarray = np.asarray(face_img)
            obj = BRISQUE(url=False)
            quality = obj.score(img=ndarray)
            print(f"Image Quality Score: {quality}")

            if quality <= 50:
                cv2.imwrite('assets\centralized_face.png', face_img)
                print("Image saved as centralized_face.png")

                # Perform anti-spoofing only
                img_path= 'assets\centralized_face.png'
                face_objs = DeepFace.extract_faces(img_path=img_path, anti_spoofing=True)

                face=face_objs[0]

                Spoof_verification= face["is_real"]
                spoof_confidence= face["antispoof_score"]
                print(Spoof_verification)
                print(spoof_confidence)
                return {"message": "Image saved as centralized_face.png", "IS image real": Spoof_verification , "quality_score": spoof_confidence}
            else:
                return {"message": "Poor image quality, retake", "quality_score": quality}

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_image()