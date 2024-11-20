from functools import lru_cache
import time
from fastapi import FastAPI, HTTPException
import requests
import psycopg2
import os
import sys
import redis
from fastapi.responses import FileResponse


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

@app.get("/args")
def get_port():
    return {"Args": sys.argv}

@app.get("/cache_compare")
def compare_cache_performance():
    TRIES = 10

    # Test no-cache: slow
    no_cache_time = 0
    for _ in range(TRIES):
        start = time.time()
        call_external_api()
        end = time.time()
        no_cache_time += end-start
    no_cache_time /= TRIES

    # Test cache: fast
    cache_time = 0
    for _ in range(TRIES):
        start = time.time()
        call_external_api_cached()
        end = time.time()
        cache_time += end - start

    cache_time /= TRIES

    return {"cache_time (avg seconds for request)": cache_time, "no_cache_time (avg seconds for request)": no_cache_time, "speed-up": no_cache_time / cache_time}


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

@app.get("/set/{key}/{value}")
def set_value(key: str, value: str, ttl: int = 300):  # default TTL 300s
    try:
        r.set(key, value, ex=ttl)
        return {"message": f"Key '{key}' set successfully with default TTL {ttl} seconds"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delete/{key}")
def delete_value(key: str):
    r.delete(key)
    return {"message": f"Key {key} deleted successfully"}

@app.get("/get/{key}")
def get_value(key: str):
    value = r.get(key)
    if value:
        current_ttl = r.ttl(key)
        if current_ttl > 0:
            new_ttl = current_ttl + 10
            r.expire(key, new_ttl)
        return {"key": key, "value": value, "new_ttl": r.ttl(key)}
    raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
@app.get("/store-image")
def store_image_in_redis():
    try:
        image_path = "static/pepe-the-frog.jpg"
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()  # bytes
        r.set("image:pepe", img_data)  # save bytes in Redis
        return {"message": "Image stored successfully in Redis"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/image")
async def get_image_from_redis():
    try:
        img_data = r.get("image:pepe")
        if not img_data:
            raise HTTPException(status_code=404, detail="Image not found in Redis")
        temp_image_path = "temp_pepe.jpg"
        with open(temp_image_path, "wb") as temp_file:
            temp_file.write(img_data)
        return FileResponse(temp_image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/ttl/{key}")
def get_key_ttl(key: str):
    try:
        ttl = r.ttl(key)
        if ttl == -2:
            raise HTTPException(status_code=404, detail=f"Key '{key}' does not exist")
        if ttl == -1:
            return {"key": key, "message": "Key exists but has no TTL"}
        return {"key": key, "ttl": ttl}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))