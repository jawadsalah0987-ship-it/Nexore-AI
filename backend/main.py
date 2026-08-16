from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import json

# استيراد الملفات المحلية التي قمنا ببرمجتها
import models
import schemas
import security
from database import engine, get_db
from ai import image_processor

# 1. تعريف تطبيق FastAPI الأساسي
app = FastAPI(title="Nexora AI")

# السماح لأي صفحة ويب بالتواصل مع الـ API (مهم للواجهة الأمامية)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. توليد جداول قاعدة البيانات تلقائياً عند التشغيل
models.Base.metadata.create_all(bind=engine)

# 3. تحديد مجلد حفظ الصور المرفوعة والتأكد من وجوده
UPLOAD_DIR = "./uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# جعل مجلد الصور متاحاً مباشرة عبر المتصفح
app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_DIR), name="uploaded_images")


# --- المسارات والـ Endpoints ---

# المسار الرئيسي (Home)
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Nexora AI",
        "status": "Running",
        "database": "Connected & Initialized"
    }


# مسار رفع ومعالجة الصور عبر الـ AI
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # توليد اسم ملف آمن وفريد (بدون مسافات أو رموز) لتفادي مشاكل الروابط
    import uuid
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # تحديد مسار حفظ الملف داخل المجلد
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # حفظ الملف الأصلي على القرص
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    # استدعاء برمجية الـ AI لمعالجة الصورة وتحليلها فوراً
    ai_results = image_processor.process_and_analyze_image(file_path)

    # تسجيل النتيجة بقاعدة البيانات
    log_entry = models.DetectionLog(
        filename=file.filename,
        saved_path=file_path,
        processed_image_path=ai_results.get("processed_image_path", ""),
        objects_detected=ai_results.get("objects_detected", 0),
        detections=json.dumps(ai_results.get("detections", []), ensure_ascii=False)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
        
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "saved_path": file_path,
        "ai_analysis": ai_results,
        "log_id": log_entry.id,
        "message": "Image uploaded and processed by Nexora AI!"
    }


# مسار عرض سجل عمليات الكشف السابقة
@app.get("/detection-logs/")
def get_detection_logs(db: Session = Depends(get_db)):
    logs = db.query(models.DetectionLog).order_by(models.DetectionLog.id.desc()).limit(50).all()
    return [
        {
            "id": log.id,
            "filename": log.filename,
            "objects_detected": log.objects_detected,
            "detections": json.loads(log.detections) if log.detections else [],
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]


# مسار تسجيل مستخدم جديد (Signup) وتشفير كلمة المرور
@app.post("/signup/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # تشفير كلمة المرور القادمة من المستخدم باستخدام Bcrypt
    hashed_pw = security.get_password_hash(user.password)
    
    # إنشاء سطر جديد في جدول المستخدمين
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_pw
    )
    
    # حفظ البيانات في قاعدة البيانات
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully!",
        "user_id": new_user.id,
        "email": new_user.email
    }