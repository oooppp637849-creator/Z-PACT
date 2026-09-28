import os
import sys
import sqlite3
import json

# Add the root directory to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def patch_database():
    print("Starting database schema patch for preferences...")
    
    db_url = settings.DATABASE_URL
    if not db_url.startswith("sqlite:///"):
        print("Script supports SQLite only for now.")
        return

    db_path = db_url.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if preferences column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "preferences" not in columns:
            print("Adding 'preferences' column to users table...")
            default_prefs = json.dumps({"theme": "dark", "chat_visible": True, "notifications": True})
            cursor.execute(f"ALTER TABLE users ADD COLUMN preferences JSON DEFAULT '{default_prefs}'")
            conn.commit()
            print("Successfully added preferences column!")
        else:
            print("preferences column already exists. No action needed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    patch_database()
