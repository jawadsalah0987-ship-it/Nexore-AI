from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="operator")


class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    saved_path = Column(String)
    processed_image_path = Column(String)
    objects_detected = Column(Integer, default=0)
    detections = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)