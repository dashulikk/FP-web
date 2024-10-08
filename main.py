from fastapi import FastAPI

app = FastAPI()

@app.get("/products/{productId}")
def get_product(productId: int):
    return {"id": str(productId), "name": f"{productId} name"}

# comment for changes
