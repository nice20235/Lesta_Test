import sqlite3
import os


DB_PATH = os.getenv("DB_PATH")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # main_user
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # main_document
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_document (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES main_user(id)
    )
    """)

    # main_collection
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_collection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES main_user(id)
    )
    """)

    # main_collection_documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_collection_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_id INTEGER NOT NULL,
        document_id INTEGER NOT NULL,
        FOREIGN KEY (collection_id) REFERENCES main_collection(id),
        FOREIGN KEY (document_id) REFERENCES main_document(id)
    )
    """)

    conn.commit()
    conn.close()
