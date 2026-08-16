from passlib.context import CryptContext

# إعداد الـ Hashing باستخدام خوارزمية bcrypt القوية
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# دالة لتشفير كلمة المرور
def get_password_hash(password: str):
    return pwd_context.hash(password)

# دالة للتحقق من تطابق كلمة المرور المُدخلة مع المشفرة
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)