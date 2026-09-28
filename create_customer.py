# create_admin.py
from app.database import SessionLocal
from app.models import User, UserRole
from app.crud import hash_password

def create_first_admin():
    db = SessionLocal()
    try:
        # التحقق إذا كان المدير موجود مسبقاً
        existing_admin = db.query(User).filter(User.email == "customer@elite.com").first()
        if existing_admin:
            print("⚠️ حساب المدير موجود بالفعل!")
            return

        # إنشاء بيانات المدير
        new_admin = User(
            full_name="محمد (المدرس)",
            email="customer@elite.com",
            password_hash=hash_password("customer123456"), # غير الباسورد زي ما تحب
            role=UserRole.CUSTOMER,
            is_active=True
        )
        
        db.add(new_admin)
        db.commit()
        
        print("✅ تم إنشاء حساب المدرس بنجاح!")
        print("✉️ الإيميل: customer@elite.com")
        print("🔑 الباسورد: customer123456")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()