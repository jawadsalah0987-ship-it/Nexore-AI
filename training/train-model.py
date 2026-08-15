from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(data="PPE-Detection-2/data.yaml", epochs=50, imgsz=640)