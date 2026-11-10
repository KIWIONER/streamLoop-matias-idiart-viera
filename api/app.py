from fastapi import FastAPI, HTTPException
from typing import List
from api.models import ProductCreate, ProductUpdate, ProductResponse
from api import db

app = FastAPI(title="Inventory API")

db.init_db()

@app.get("/inventory", response_model=List[ProductResponse], summary="Obtener todos los productos")
def get_inventory():
    return db.read_all_products()

@app.post("/inventory", response_model=ProductResponse, summary="Añadir un nuevo producto")
def add_product(product: ProductCreate):
    new_product = db.create_product(product.name, product.quantity, product.unit)
    return new_product


@app.patch("/inventory/{product_id}", response_model=ProductResponse, summary="Actualizar stock de un producto")
def update_product(product_id: str, update_data: ProductUpdate):
    try:
        updated_product = db.update_product_stock(product_id, update_data.delta)
        return updated_product
    except KeyError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/inventory/alerts", response_model=List[ProductResponse], summary="Obtener productos con bajo stock")
def get_alerts(threshold: int = 10):
    return db.get_low_stock_alerts(threshold)