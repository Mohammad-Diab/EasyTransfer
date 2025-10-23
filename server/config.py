from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = str((BASE_DIR / "db.sqlite3").resolve())
MAX_CONTACTS_PER_ACCOUNT = 5