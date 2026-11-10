import csv
import os
import uuid
from typing import List, Dict

DB_FILE = "products.csv"
HEADERS = ["id", "name", "quantity", "unit"]

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def read_all_products() -> List[Dict]:
    init_db()
    products = []
    with open(DB_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["quantity"] = int(row["quantity"])
            products.append(row)
    return products

def write_all_products(products: List[Dict]):
    with open(DB_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(products)

def create_product(name: str, quantity: int, unit: str) -> Dict:
    products = read_all_products()
    new_id = str(uuid.uuid4())
    new_product = {
        "id": new_id,
        "name": name,
        "quantity": quantity,
        "unit": unit
    }
    products.append(new_product)
    write_all_products(products)
    return new_product

def update_product_stock(product_id: str, delta: int) -> Dict:
    products = read_all_products()
    for p in products:
        if p["id"] == product_id:
            new_quantity = p["quantity"] + delta
            if new_quantity < 0:
                raise ValueError("La cantidad final no puede ser negativa")
            p["quantity"] = new_quantity
            write_all_products(products)
            return p
    raise KeyError("Producto no encontrado")

def get_low_stock_alerts(threshold: int = 10) -> List[Dict]:
    products = read_all_products()
    alerts = [p for p in products if p["quantity"] < threshold]
    return alerts
