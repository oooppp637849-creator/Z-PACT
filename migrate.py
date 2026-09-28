from app.database import engine
from app.models import Base
import sqlalchemy as sa

def migrate():
    # 1. Create new tables (like layout_presets)
    Base.metadata.create_all(engine)
    print("New tables created (if any)")

    # 2. Add new columns
    with engine.connect() as conn:
        # User.coins
        try:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN coins NUMERIC(10, 2) DEFAULT 0.0"))
            conn.commit()
            print("Added coins to users")
        except Exception as e:
            print(f"User.coins might already exist: {e}")

        # Material.price_coins
        try:
            conn.execute(sa.text("ALTER TABLE materials ADD COLUMN price_coins NUMERIC(10, 2) DEFAULT 0.0"))
            conn.commit()
            print("Added price_coins to materials")
        except Exception as e:
            print(f"Material.price_coins might already exist: {e}")

        # Purchase.payment_method
        try:
            conn.execute(sa.text("ALTER TABLE purchases ADD COLUMN payment_method VARCHAR(20) DEFAULT 'money'"))
            conn.commit()
            print("Added payment_method to purchases")
        except Exception as e:
            print(f"Purchase.payment_method might already exist: {e}")
        # User.phone
        try:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
            conn.commit()
            print("Added phone to users")
        except Exception as e:
            print(f"User.phone might already exist: {e}")

        # User.profile_picture_path
        try:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN profile_picture_path VARCHAR(500)"))
            conn.commit()
            print("Added profile_picture_path to users")
        except Exception as e:
            print(f"User.profile_picture_path might already exist: {e}")

        # User.total_spent
        try:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN total_spent NUMERIC(10, 2) DEFAULT 0.0"))
            conn.commit()
            print("Added total_spent to users")
        except Exception as e:
            print(f"User.total_spent might already exist: {e}")

        # Material.cover_image_path
        try:
            conn.execute(sa.text("ALTER TABLE materials ADD COLUMN cover_image_path VARCHAR(500)"))
            conn.commit()
            print("Added cover_image_path to materials")
        except Exception as e:
            print(f"Material.cover_image_path might already exist: {e}")

if __name__ == "__main__":
    migrate()
