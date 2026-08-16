from ultralytics import YOLO
from PIL import Image
import os

model = YOLO("ppe_model.pt")

def process_and_analyze_image(file_path: str):
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    img = Image.open(file_path).convert("RGB")
    results = model(img)

    detected_objects = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = [round(float(v), 1) for v in box.xyxy[0]]

            detected_objects.append({
                "object": class_name,
                "confidence": round(confidence, 2),
                "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            })

    dir_name = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    processed_file_path = os.path.join(dir_name, f"detected_{base_name}.jpg")
    results[0].save(filename=processed_file_path)

    return {
        "objects_detected": len(detected_objects),
        "detections": detected_objects,
        "processed_image_path": processed_file_path,
        "status": "Object detection completed successfully"
    }