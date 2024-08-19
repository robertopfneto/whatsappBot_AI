from vidgear.gears import CamGear
import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolov8n-seg.pt')

# Start the video stream
stream = CamGear(source='https://www.youtube.com/watch?v=fQ-gRjOuwc4', stream_mode=True, logging=True).start()

# Desired resolution
desired_width = 1920
desired_height = 1080

while True:
    frame = stream.read()

    if frame is None:
        break

    # Resize the frame to the desired resolution
    resized_frame = cv2.resize(frame, (desired_width, desired_height))

    # Run YOLOv8 inference on the resized frame
    results = model(resized_frame)

    # Visualize the results on the resized frame
    annotated_frame = results[0].plot()

    # Display the annotated frame
    cv2.imshow("YOLOv8 Inference", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
stream.stop()
