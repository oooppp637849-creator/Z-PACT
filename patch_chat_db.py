import os
import sys
import sqlite3

# Add the root directory to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def patch_database():
    print("Starting database schema patch for chat_messages...")
    
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

        # Check if reply_to_id column exists in chat_messages table
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "reply_to_id" not in columns:
            print("Adding 'reply_to_id' column to chat_messages table...")
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN reply_to_id INTEGER REFERENCES chat_messages(id)")
            conn.commit()
            print("Successfully added reply_to_id column!")
        else:
            print("reply_to_id column already exists. No action needed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    patch_database()
