from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_app.endpoints.auth import create_access_token, get_current_user
from fastapi_app.endpoints.database import init_db  
from pydantic import BaseModel
from fastapi import Response
import sqlite3
import hashlib
import os


router = APIRouter()
DB_PATH = os.getenv("DB_PATH")

def get_db_connection():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class UserAuth(BaseModel):
    username: str
    password: str

class PasswordUpdate(BaseModel):
    password: str
    
@router.post("/register", summary="Создание пользователя")
def register_user(user: UserAuth):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Чтобы fetchone() возвращал словарь
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM main_user WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    cursor.execute("INSERT INTO main_user (username, password) VALUES (?, ?)",
                   (user.username, hash_password(user.password)))
    conn.commit()

    user_id = cursor.lastrowid

    cursor.execute("SELECT * FROM main_user WHERE id = ?", (user_id,))
    new_user = cursor.fetchone()
    conn.close()

    return dict(new_user)  # Преобразуем строку в обычный словарь и возвращаем


@router.post("/login", summary="Логин пользователя")
def login_user(user: UserAuth):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(user.password)
    cursor.execute("SELECT id FROM main_user WHERE username = ? AND password = ?",
                   (user.username, hashed_password))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    access_token = create_access_token(data={"sub": str(row["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/update", summary="Изменение пароля")
def update_password(pw: PasswordUpdate, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE main_user SET password = ? WHERE id = ?",
                   (hash_password(pw.password), user_id))
    conn.commit()
    conn.close()
    return {"message": "Пароль обновлён"}


@router.delete("/delete", summary="Удаление пользователя")
def delete_user(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM main_document WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM main_collection_documents WHERE collection_id IN (SELECT id FROM main_collection WHERE user_id = ?)", (user_id,))
    cursor.execute("DELETE FROM main_collection WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM main_user WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()
    return {"message": "Пользователь и все его данные удалены"}


@router.get("/all", summary="Получение всех пользователей")
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM main_user")  # Не включаем пароли по соображениям безопасности
    users = cursor.fetchall()
    conn.close()

    return [dict(user) for user in users]



@router.get("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="access_token", httponly=True)
    return {"message": "Выход выполнен. Cookie удалена."}


