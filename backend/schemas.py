from pydantic import BaseModel

# هيكل البيانات المطلوب من المستخدم إرسالها عند التسجيل
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str