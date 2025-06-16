from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi_app.endpoints.auth import get_current_user
from fastapi_app.endpoints.database import init_db  
from collections import Counter
from main.models import UploadedFile
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

import shutil
import uuid
import sqlite3
import os
import math
import re
import heapq


router = APIRouter()
DB_PATH = os.getenv("DB_PATH")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

def get_db_connection():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/", summary="Список документов пользователя")
def list_documents(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM main_document WHERE user_id = ?", (user_id,))
    docs = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
    conn.close()
    return docs


@router.get("/{document_id}", summary="Содержимое документа")
def get_document(document_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path, user_id FROM main_document WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or row["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    if not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail="Файл отсутствует")
    with open(row["path"], "r", encoding="utf-8") as f:
        return {"content": f.read()}
    


@router.get("/{document_id}/statistics", summary="TF/IDF статистика по документу")
def document_statistics(document_id: int, user_id: int = Depends(get_current_user)):
    def tokenize(text):
        return re.findall(r"\b\w{2,}\b", text.lower())

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем путь к текущему документу
    cursor.execute(
        "SELECT path FROM main_document WHERE id = ? AND user_id = ?",
        (document_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Документ не найден")

    path = row["path"]
    if not os.path.exists(path):
        conn.close()
        raise HTTPException(status_code=404, detail="Файл не найден")

    with open(path, "r", encoding="utf-8") as f:
        current_text = f.read()

    current_tokens = tokenize(current_text)
    total_terms = len(current_tokens)
    tf_counts = Counter(current_tokens)

    # Получаем пути ко всем другим документам пользователя
    cursor.execute(
        "SELECT path FROM main_document WHERE user_id = ? AND id != ?",
        (user_id, document_id)
    )
    other_rows = cursor.fetchall()
    conn.close()

    total_docs = 1  # текущий документ
    word_doc_occurrences = Counter()

    for row in other_rows:
        other_path = row["path"]
        if not os.path.exists(other_path):
            continue
        with open(other_path, "r", encoding="utf-8") as f:
            text = f.read()
            tokens = set(tokenize(text))
            word_doc_occurrences.update(tokens)
            total_docs += 1

    # Учитываем текущий документ тоже
    for word in set(current_tokens):
        word_doc_occurrences[word] += 1

    # TF-IDF для 50 наименее частых слов (по TF)
    tf_sorted = sorted(tf_counts.items(), key=lambda x: x[1])[:50]
    statistics = []

    for word, count in tf_sorted:
        tf = round(count / total_terms, 6)
        idf = round(math.log(total_docs / word_doc_occurrences[word]), 6)
        statistics.append({
            "word": word,
            "tf": tf,
            "idf": idf
        })

    return {
        "document_id": document_id,
        "statistics": statistics
    }


@router.delete("/{document_id}", summary="Удалить документ")
def delete_document(document_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path, user_id FROM main_document WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    if not row or row["user_id"] != user_id:
        conn.close()
        raise HTTPException(status_code=403, detail="Нет доступа")
    if os.path.exists(row["path"]):
        os.remove(row["path"])
    cursor.execute("DELETE FROM main_document WHERE id = ?", (document_id,))
    cursor.execute("DELETE FROM main_collection_documents WHERE document_id = ?", (document_id,))
    conn.commit()
    conn.close()
    return {"message": "Документ удалён"}


@router.post("/upload", summary="Загрузить документ")
def upload_document(file: UploadFile = File(...), user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Убедимся, что директория существует
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Уникальное имя файла
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Сохраняем запись в БД
    cursor.execute(
        "INSERT INTO main_document (name, path, user_id) VALUES (?, ?, ?)",
        (file.filename, file_path, user_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Документ загружен", "filename": file.filename}



class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text: str):
    if not text:
        return None
    
    freq = Counter(text)
    heap = [HuffmanNode(char=ch, freq=f) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(freq=node1.freq + node2.freq, left=node1, right=node2)
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def build_codes(node: HuffmanNode, prefix="", code_map=None):
    if code_map is None:
        code_map = {}
    if node is None:
        return code_map
    if node.char is not None:
        code_map[node.char] = prefix
    build_codes(node.left, prefix + "0", code_map)
    build_codes(node.right, prefix + "1", code_map)
    return code_map

def encode_text(text: str, code_map: dict) -> str:
    return ''.join(code_map[char] for char in text)

@router.get("/{document_id}/huffman")
async def get_huffman_encoded(document_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM main_document WHERE id = ? AND user_id = ?", (document_id, user_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Документ не найден или нет доступа")
    
    path = os.path.abspath(row["path"])
    print("Абсолютный путь:", path)
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден на диске")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Ошибка декодирования файла (возможно, неверная кодировка)")

    root = build_huffman_tree(content)
    if not root:
        raise HTTPException(status_code=400, detail="Не удалось построить дерево Хаффмана (пустой файл?)")

    code_map = build_codes(root)
    encoded = encode_text(content, code_map)

    return {
        "encoded_text": encoded,
        "code_table": code_map
    }