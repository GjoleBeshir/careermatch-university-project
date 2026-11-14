"""Wait up to 30 seconds for PostgreSQL before seeding."""
import time
from sqlalchemy import text
from app.database import engine

def main():
    for attempt in range(30):
        try:
            with engine.connect() as db:
                db.execute(text("SELECT 1"))
            print("Database ready.")
            return
        except Exception:
            if attempt == 29:
                raise SystemExit("Database unavailable after 30 seconds. Check Docker and DATABASE_URL.")
            time.sleep(1)

if __name__ == "__main__":
    main()
