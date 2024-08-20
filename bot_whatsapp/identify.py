import cv2
from ultralytics import YOLO
from send_message import send_identification_results

model = YOLO('yolov8n-seg.pt')

def process_video(video_filename, from_number):
    print(f"Processing video: {video_filename}")  

    identified_objects = {}

    cap = cv2.VideoCapture(video_filename)

    if not cap.isOpened():
        print(f"Error opening video file: {video_filename}")  
        return

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1
        print(f"Processing frame {frame_count}...")  

        try:
            results = model(frame)
            print(f"Results: {results}")  
        except Exception as e:
            print(f"Error in inference: {e}")  
            continue

        for result in results:
            try:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = box.conf[0]
                    class_name = model.names[class_id]

                    if class_name not in identified_objects:
                        identified_objects[class_name] = []

                    identified_objects[class_name].append(confidence)
            except AttributeError as e:
                print(f"Error processing results: {e}")  

    cap.release()
    print("Video processing completed.")  
    send_identification_results(identified_objects, from_number)
