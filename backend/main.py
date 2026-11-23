from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import json

import models
import schemas
import security
from database import engine, get_db
from ai import image_processor
from safety_engine import analyze_safety


# ==========================================
# 1. APPLICATION SETUP
# ==========================================

app = FastAPI(title="Nexora AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


# ==========================================
# 2. IMAGE STORAGE
# ==========================================

UPLOAD_DIR = "./uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploaded_images",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploaded_images"
)


# ==========================================
# 3. HOME ENDPOINT
# ==========================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Nexora AI",
        "status": "Running",
        "database": "Connected & Initialized"
    }


# ==========================================
# 4. IMAGE UPLOAD & AI DETECTION
# ==========================================

@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    import uuid

    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4().hex}{file_ext}"

    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save uploaded image
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # AI Object Detection
    ai_results = image_processor.process_and_analyze_image(file_path)

    # Safety Analysis
    safety_analysis = analyze_safety(
        ai_results.get("detections", [])
    )

    # Save detection results to database
    log_entry = models.DetectionLog(
        filename=file.filename,
        saved_path=file_path,
        processed_image_path=ai_results.get(
            "processed_image_path", ""
        ),
        objects_detected=ai_results.get(
            "objects_detected", 0
        ),
        detections=json.dumps(
            ai_results.get("detections", []),
            ensure_ascii=False
        )
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    # API Response
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "saved_path": file_path,

        "ai_analysis": ai_results,
        "safety_analysis": safety_analysis,

        "log_id": log_entry.id,
        "message": "Image uploaded and processed by Nexora AI!"
    }


# ==========================================
# 5. DETECTION HISTORY
# ==========================================

@app.get("/detection-logs/")
def get_detection_logs(db: Session = Depends(get_db)):

    logs = (
        db.query(models.DetectionLog)
        .order_by(models.DetectionLog.id.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": log.id,
            "filename": log.filename,
            "objects_detected": log.objects_detected,
            "detections": json.loads(log.detections)
            if log.detections else [],
            "created_at": log.created_at.isoformat()
            if log.created_at else None
        }
        for log in logs
    ]


# ==========================================
# 6. USER REGISTRATION
# ==========================================

@app.post("/signup/")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    hashed_pw = security.get_password_hash(user.password)

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully!",
        "user_id": new_user.id,
        "email": new_user.email
    }