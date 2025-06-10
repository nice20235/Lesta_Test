import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


from fastapi import FastAPI, Request
from starlette.applications import Starlette
from starlette.routing import Mount
from fastapi.staticfiles import StaticFiles
from collections import deque
from fastapi_app.endpoints.users import router as users_router
from fastapi_app.endpoints.documents import router as documents_router
from fastapi_app.endpoints.my_collections import router as collections_router

import sqlite3
import datetime
import json
import threading
import time



from django.core.asgi import get_asgi_application


fastapi_app = FastAPI()
django_app = get_asgi_application()


fastapi_app.include_router(users_router, prefix="/users", tags=["Users"])
fastapi_app.include_router(documents_router, prefix="/documents", tags=["Documents"])
fastapi_app.include_router(collections_router, prefix="/collections", tags=["Collections"])


APP_VERSION = "1.0.0"


DB_PATH = "baza.db"
UPLOAD_DIR = "media/files"




def init_db():
    conn = sqlite3.connect("baza.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS main_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()



request_lock = threading.Lock()
response_times = []  
request_timestamps = deque()  


def save_metrics(metrics_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            data TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO metrics (timestamp, data) VALUES (?, ?)
    ''', (datetime.datetime.now().isoformat(), json.dumps(metrics_data)))
    conn.commit()
    conn.close()

def get_directory_size_mb(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)  



@fastapi_app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    global response_times, request_timestamps

    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    with request_lock:
        response_times.append(duration)
        now = time.time()
        request_timestamps.append(now)


        five_min_ago = now - 300
        while request_timestamps and request_timestamps[0] < five_min_ago:
            request_timestamps.popleft()

    return response

@fastapi_app.get("/status")
def get_status():
    return {"status": "OK"}

@fastapi_app.get("/metrics")
def get_metrics():
    with request_lock:
        avg_response_time = round(sum(response_times) / len(response_times), 4) if response_times else 0
        request_count_last_5min = len(request_timestamps)


    metrics_data = {
        "avg_response_time": avg_response_time,
        "request_count_last_5min": request_count_last_5min,
    }

    save_metrics(metrics_data)
    return metrics_data

@fastapi_app.get("/version")
def get_version():
    return {"version": APP_VERSION}



app = Starlette(routes=[
    Mount("/api", app=fastapi_app),
    Mount("/", app=django_app),
])

app.mount("/static", StaticFiles(directory="static"), name="static")

