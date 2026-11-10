from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(..., description="Nombre del producto")
    quantity: int = Field(..., ge=0, description="Cantidad en stock")
    unit: str = Field(..., description="Unidad de medida (ej. kg, litros, unidades)")

class ProductUpdate(BaseModel):
    delta: int = Field(..., description="Cambio en la cantidad. Positivo para entradas, negativo para salidas.")

class ProductResponse(BaseModel):
    id: str
    name: str
    quantity: int
    unit: str
