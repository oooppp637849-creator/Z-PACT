# ================================================================
# app/config.py — إعدادات التطبيق والمتغيرات البيئية
# ================================================================

import os
from dotenv import load_dotenv

# تحديد المسار الأساسي للمشروع
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# مسار ملف .env بشكل مطلق لضمان قراءته دائماً
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

def _get_or_create_jwt_secret():
    env_secret = os.getenv("JWT_SECRET_KEY")
    if env_secret and env_secret != "change-me-in-production-please":
        return env_secret
    secret_file = os.path.join(BASE_DIR, ".jwt_secret")
    if os.path.exists(secret_file):
        try:
            with open(secret_file, "r", encoding="utf-8") as f:
                s = f.read().strip()
                if len(s) >= 32:
                    return s
        except Exception:
            pass
    import secrets
    new_secret = secrets.token_hex(32)
    try:
        with open(secret_file, "w", encoding="utf-8") as f:
            f.write(new_secret)
    except Exception:
        pass
    return new_secret

class Settings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY = _get_or_create_jwt_secret()
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_H = 24
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    BASE_DIR = BASE_DIR

    @property
    def DATABASE_URL(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        if self.ENVIRONMENT == "production":
            return "sqlite:////.data/webpdf_elite.db"
        # في بيئة التطوير المحلية، نحافظ على الداتا الحالية إذا كانت موجودة، أو ننشئها داخل storage
        if os.name == "nt" and os.path.exists("C:/.data/webpdf_elite.db"):
            return "sqlite:////.data/webpdf_elite.db"
        return f"sqlite:///{os.path.join(self.BASE_DIR, 'storage', 'webpdf_elite.db')}"

    @property
    def DATABASE_PATH(self) -> str:
        """تحويل DATABASE_URL إلى مسار ملف مطلق (لأغراض SQLite)"""
        url = self.DATABASE_URL
        if not url.startswith("sqlite:///"):
            return url # مش SQLite أصلاً
            
        # إزالة البادئة "sqlite:///" (أول 10 حروف)
        path = url[10:]
        
        # 1. إذا كان مساراً مطلقاً (يبدأ بـ / في لينكس أو C:\ في ويندوز)
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return os.path.abspath(path)
            
        # 2. إذا كان يبدأ بـ ./ نعتبره نسبياً لـ BASE_DIR
        if path.startswith('./'):
            return os.path.abspath(os.path.join(self.BASE_DIR, path[2:]))
            
    # 3. أي مسار آخر نعتبره نسبياً لـ BASE_DIR
        return os.path.abspath(os.path.join(self.BASE_DIR, path))

    @property
    def STORAGE_DIR(self) -> str:
        """مسار تخزين الملفات (Originals, Stamped, Previews)"""
        if self.ENVIRONMENT == "production":
            # في الإنتاج على Railway، نستخدم المجلد داخل الـ Volume المستمر
            path = "/.data/storage"
        else:
            path = os.path.join(self.BASE_DIR, "storage")
        
        os.makedirs(path, exist_ok=True)
        return path

settings = Settings()
