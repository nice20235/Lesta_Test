from fastapi import APIRouter, HTTPException, Depends
from .auth import get_current_user
from .database import init_db 
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
import os

router = APIRouter()
DB_PATH = os.getenv("DB_PATH")

def get_db_connection():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/", summary="Список коллекций")
def list_collections(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM main_collection WHERE user_id = ?", (user_id,))
    collections = []
    for col in cursor.fetchall():
        cursor.execute("SELECT document_id FROM main_collection_documents WHERE collection_id = ?", (col["id"],))
        docs = [row["document_id"] for row in cursor.fetchall()]
        collections.append({"id": col["id"], "name": col["name"], "documents": docs})
    conn.close()
    return collections

@router.get("/{collection_id}", summary="Документы в коллекции")
def collection_documents(collection_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM main_collection WHERE id = ?", (collection_id,))
    owner = cursor.fetchone()
    if not owner or owner["user_id"] != user_id:
        conn.close()
        raise HTTPException(status_code=403, detail="Нет доступа")
    cursor.execute("SELECT document_id FROM main_collection_documents WHERE collection_id = ?", (collection_id,))
    doc_ids = [row["document_id"] for row in cursor.fetchall()]
    conn.close()
    return {"documents": doc_ids}

@router.post("/{collection_id}/{document_id}", summary="Добавить документ в коллекцию")
def add_document_to_collection(collection_id: int, document_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM main_collection WHERE id = ?", (collection_id,))
    owner = cursor.fetchone()
    if not owner or owner["user_id"] != user_id:
        conn.close()
        raise HTTPException(status_code=403, detail="Нет доступа")
    cursor.execute("SELECT 1 FROM main_collection_documents WHERE collection_id = ? AND document_id = ?", (collection_id, document_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Документ уже добавлен")
    cursor.execute("INSERT INTO main_collection_documents (collection_id, document_id) VALUES (?, ?)", (collection_id, document_id))
    conn.commit()
    conn.close()
    return {"message": "Документ добавлен"}


@router.delete("/{collection_id}/{document_id}", summary="Удалить документ из коллекции")
def remove_document_from_collection(collection_id: int, document_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM main_collection WHERE id = ?", (collection_id,))
    owner = cursor.fetchone()
    if not owner or owner["user_id"] != user_id:
        conn.close()
        raise HTTPException(status_code=403, detail="Нет доступа")
    cursor.execute("DELETE FROM main_collection_documents WHERE collection_id = ? AND document_id = ?", (collection_id, document_id))
    conn.commit()
    conn.close()
    return {"message": "Документ удалён из коллекции"}


@router.get("/{collection_id}/statistics", summary="TF-IDF по коллекции")
def collection_statistics(collection_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем все документы пользователя (для IDF)
    cursor.execute("SELECT path FROM main_document WHERE user_id = ?", (user_id,))
    all_user_doc_rows = cursor.fetchall()

    all_user_docs = []
    for row in all_user_doc_rows:
        if os.path.exists(row["path"]):
            with open(row["path"], "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    all_user_docs.append(text)

    if not all_user_docs:
        conn.close()
        raise HTTPException(status_code=400, detail="У пользователя нет документов для расчёта IDF")

    # Получаем документы из коллекции (для TF)
    cursor.execute("""
        SELECT d.path
        FROM main_document d
        JOIN main_collection_documents cd ON cd.document_id = d.id
        WHERE cd.collection_id = ? AND d.user_id = ?
    """, (collection_id, user_id))
    collection_doc_rows = cursor.fetchall()
    conn.close()

    collection_docs = []
    for row in collection_doc_rows:
        if os.path.exists(row["path"]):
            with open(row["path"], "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    collection_docs.append(text)

    if not collection_docs:
        raise HTTPException(status_code=400, detail="Коллекция пуста или документы недоступны")

    # TF: как будто все документы в коллекции — один документ
    merged_collection_text = " ".join(collection_docs)

    # Обучаем IDF на всех документах пользователя
    vectorizer = TfidfVectorizer(use_idf=True)
    vectorizer.fit(all_user_docs)

    # Преобразуем объединённую коллекцию (TF * IDF)
    tfidf_vector = vectorizer.transform([merged_collection_text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_vector.toarray()[0]

    # Получаем IDF отдельно
    idf_scores = dict(zip(feature_names, vectorizer.idf_))
    tfidf_data = []

    for idx, word in enumerate(feature_names):
        tf_value = scores[idx] / idf_scores[word]  # tf = tfidf / idf
        tfidf_data.append({
            "word": word,
            "tf": round(tf_value, 6),
            "idf": round(idf_scores[word], 6)
        })

    # Сортируем по tf (редкие слова в коллекции) и берём 50
    tfidf_data.sort(key=lambda x: x["tf"])

    return {
        "collection_id": collection_id,
        "rare_words": tfidf_data[:50]
    }