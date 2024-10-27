import cv2

cap = cv2.VideoCapture('http://192.168.213.47:8080/video')
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Video Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()