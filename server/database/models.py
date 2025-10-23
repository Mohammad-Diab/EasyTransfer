import sqlite3
from config import DB_NAME
from constants import STATUS_PENDING
from datetime import datetime, timezone


class Database:
    """Database connection context manager"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()


def init_db():
    """Initialize database tables"""
    with Database() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            request_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (request_id) REFERENCES requests (id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL CHECK(length(phone_number) <= 14),
            name VARCHAR(50) NOT NULL,
            date_added TEXT NOT NULL
        )
        """)


class RequestModel:
    """Request database operations"""
    
    @staticmethod
    def add(account_id, phone_number, amount):
        with Database() as c:
            created_at = datetime.now(timezone.utc).isoformat()

            c.execute(
                "INSERT INTO requests (account_id, phone_number, amount, created_at) VALUES (?, ?, ?, ?)",
                (account_id, phone_number, amount, created_at)
            )
            return c.lastrowid

    @staticmethod
    def get_next(account_id):
        with Database() as c:
            c.execute(
                "SELECT id, phone_number, amount FROM requests WHERE status=? AND account_id=? ORDER BY created_at ASC LIMIT 1",
                (STATUS_PENDING, account_id)
            )
            return c.fetchone()

    @staticmethod
    def get_by_id(account_id, request_id):
        with Database() as c:
            c.execute(
                "SELECT id, phone_number, amount, status FROM requests WHERE id=? AND account_id=?",
                (request_id, account_id)
            )
            return c.fetchone()

    @staticmethod
    def get_by_account(account_id):
        with Database() as c:
            c.execute(
                "SELECT id, phone_number, amount, status, created_at FROM requests WHERE account_id=? ORDER BY created_at DESC",
                (account_id,)
            )
            return c.fetchall()

    @staticmethod
    def update_status(account_id, request_id, status):
        with Database() as c:
            c.execute(
                "UPDATE requests SET status=? WHERE id=? AND account_id=?",
                (status, request_id, account_id)
            )


class ResultModel:
    """Result database operations"""
    
    @staticmethod
    def add(account_id, request_id, status, message):
        with Database() as c:
            created_at = datetime.now(timezone.utc).isoformat()
            c.execute(
                "INSERT INTO results (account_id, request_id, status, message, created_at) VALUES (?, ?, ?, ?, ?)",
                (account_id, request_id, status, message, created_at)
            )


class ContactModel:
    """Contact database operations"""
    
    @staticmethod
    def add(account_id, phone_number, name):
        with Database() as c:
            date_added = datetime.now(timezone.utc).isoformat()
            c.execute(
                "INSERT INTO contacts (account_id, phone_number, name, date_added) VALUES (?, ?, ?, ?)",
                (account_id, phone_number, name, date_added)
            )
            return c.lastrowid

    @staticmethod
    def get_by_account(account_id):
        with Database() as c:
            c.execute(
                "SELECT id, phone_number, name, date_added FROM contacts WHERE account_id=? ORDER BY date_added DESC",
                (account_id,)
            )
            return c.fetchall()

    @staticmethod
    def get_by_id(account_id, contact_id):
        with Database() as c:
            c.execute(
                "SELECT id, phone_number, name, date_added FROM contacts WHERE id=? AND account_id=?",
                (contact_id, account_id)
            )
            return c.fetchone()

    @staticmethod
    def delete(account_id, contact_id):
        with Database() as c:
            c.execute("DELETE FROM contacts WHERE id=? AND account_id=?", (contact_id, account_id))
