import cv2
import threading

# Flag to control the running of the loop
running = True

def input_listener():
    global running
    while True:
        command = input()  # wait for input from SSH terminal
        if command.strip().lower() == 'stop':
            running = False
            break

# Initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open the webcam (0 is default webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()

# Start the input listener thread so we can type 'stop' to end the loop
listener_thread = threading.Thread(target=input_listener, daemon=True)
listener_thread.start()

print("Starting person detection. Type 'stop' and press Enter to quit.")

while running:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Detect people
    rects, weights = hog.detectMultiScale(frame, winStride=(8,8), padding=(16,16), scale=1.05)

    # Draw rectangles on detected people
    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    # Show the frame
    cv2.imshow('Person Detection', frame)

    # Wait 1ms for 'q' or until window closes
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Program stopped.")