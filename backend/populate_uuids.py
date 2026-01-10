import os
import sys
import uuid

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User

def populate_uuids():
    """Populates the uuid field for existing users."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.uuid == None).all()
        if not users:
            print("✅ All users already have UUIDs.")
            return

        print(f"Found {len(users)} users without UUIDs. Populating...")

        for user in users:
            user.uuid = uuid.uuid4()
            print(f"  - Generated UUID for user: {user.email}")

        db.commit()
        print("✅ Successfully populated UUIDs for all users.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error populating UUIDs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_uuids()
