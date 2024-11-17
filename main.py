from functools import lru_cache

import time
from fastapi import FastAPI, HTTPException
import requests
import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        dbname="web_app_db", user="postgres", password=os.getenv("DB_PASSWORD"), host="localhost"
    )
    return conn

app = FastAPI()
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.get("/products/{productId}")
def get_product(productId: int):
    return {"id": str(productId), "name": f"{productId} name"}
@app.get("/external-api")
def call_external_api():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    return response.json()

@lru_cache
def call_external_api_cached():
    return call_external_api()

@app.get("/users/")
def fetch_users():
    return get_users()


def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return [{"id": row[0], "name": row[1], "email": row[2]} for row in users]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache_compare")
def compare_cache_performance():
    TRIES = 10
    no_cache_time = 0
    for _ in range(TRIES):
        start = time.time()
        call_external_api()
        end = time.time()
        no_cache_time += end-start
    no_cache_time /= TRIES

    cache_time = 0
    for _ in range(TRIES):
        start = time.time()
        call_external_api_cached()
        end = time.time()
        cache_time += end - start

    cache_time /= TRIES

    return {"cache_time": cache_time, "no_cache_time": no_cache_time, "speed-up": no_cache_time / cache_time}
