from fastapi import FastAPI
import requests

app = FastAPI()
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.get("/products/{productId}")
def get_product(productId: int):
    a ="123123"
    b = "123123"
    c = "123123"
    d = "123123"
    return {"id": str(productId), "name": f"{productId} name"}
@app.get("/external-api")
def call_external_api():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    return response.json()
