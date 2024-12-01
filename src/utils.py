import cv2

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
