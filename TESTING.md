# Pruebas de Inventario (Inventory API)

Este documento describe la estrategia de pruebas unitarias implementada para la API de Inventario.

## Ejecución de Pruebas

Para ejecutar toda la batería de pruebas y ver la cobertura, usa el siguiente comando desde la raíz del proyecto:

```bash
python -m pytest --cov=api --cov-report=term-missing
```

## Casos de Prueba Implementados

### 1. `GET /inventory` y `GET /inventory/alerts` (Módulo: `test_inventory_get.py`)
- **Happy Path:** Se obtienen todos los productos (lista completa). Se obtienen los productos bajo el umbral (alerts).
- **Edge Case:** Solicitar alertas con `threshold=0`.
- **Failure Mode:** Simular que la base de datos está inaccesible o devuelve errores inesperados.

### 2. `POST /inventory` (Módulo: `test_inventory_post.py`)
- **Happy Path:** Se crea un producto correctamente con todos sus datos válidos.
- **Edge Case:** Valores extremos (ej. `quantity=0`, producto duplicado pero manejado).
- **Failure Mode:** Enviar un cuerpo de solicitud inválido (falta un campo requerido como `name` o `quantity`).

### 3. `PATCH /inventory/{product_id}` (Módulo: `test_inventory_patch.py`)
- **Happy Path:** Se incrementa o reduce el stock de forma correcta usando el `delta`.
- **Edge Case:** Se reduce el stock hasta dejarlo exactamente en `0`.
- **Failure Mode:** 
  - Intentar reducir el stock más de lo disponible (debe generar error 400).
  - Intentar actualizar un `product_id` inexistente (debe generar error 404).

## Decisiones de Diseño

1. **Uso de TestClient:** Se utilizó `TestClient` de FastAPI y `httpx` para simular las peticiones sin tener que levantar el servidor real en cada prueba.
2. **Aislamiento:** Al no tener una base de datos relacional tradicional (usamos un CSV), las pruebas deben interactuar cuidadosamente con la capa de datos (`api.db`). En `conftest.py`, aseguramos un entorno aislado o mockeado para que las pruebas no sobreescriban tu `products.csv` real de producción.
