from fastapi import FastAPI

app = FastAPI()

@app.get("/products/{productId}")
def get_product(productId: int):
    a ="123123"
    b = "123123"
    c = "123123"
    d = "123123"
    return {"id": str(productId), "name": f"{productId} name"}

# comment for changes
# test1
# texst