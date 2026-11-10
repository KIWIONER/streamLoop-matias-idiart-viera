# Plan de Implementación: Batería de Pruebas (Adaptado a Inventory API)

> [!NOTE]
> Según el documento `strategy.md`, el reto original hablaba de una API de *autenticación*. Sin embargo, en tu proyecto actual la API está orientada a *Inventario* (`/inventory`). He adaptado el plan para cumplir exactamente con los mismos requisitos de calidad, estructura y cobertura, pero aplicándolos a los endpoints reales de tu aplicación.

Para asegurar un diseño robusto del plan, he aplicado tres metodologías avanzadas de diseño de software:
1. **Los 3 Expertos (Panel de Revisión)**: Simulando perspectivas de un QA Engineer, un Security/Edge Case Tester y el CTO.
2. **Self-Refinement Loop**: Iteración sobre los casos de prueba para eliminar redundancias y maximizar la cobertura lógica.
3. **Red Teaming (El tercer método)**: Buscar intencionadamente cómo romper la API enviando datos anómalos o forzando estados inválidos en la base de datos.

---

## 🙋‍♂️ Open Questions

> [!IMPORTANT]
> **Aclaración sobre el Dominio:** Como mencioné, `strategy.md` menciona endpoints de Auth (registro, login, token). Nuestra API tiene: `GET /inventory`, `POST /inventory`, `PATCH /inventory/{id}` y `GET /inventory/alerts`. 
> ¿Estás de acuerdo con aplicar el plan de pruebas a la API de **Inventario**, o prefieres que primero construyamos los endpoints de Auth y luego los probemos?

---

## 🛠 Metodología Aplicada

### 1. Panel de los 3 Expertos
- **Experto 1 (QA Lead):** "Debemos asegurar que cada endpoint tenga un *Happy Path* claro que demuestre que la funcionalidad básica opera 100% como se espera."
- **Experto 2 (Edge Case Tester):** "El foco debe estar en los límites: ¿qué pasa al intentar actualizar el stock de un producto que no existe? ¿O cuando el `threshold` de alertas es negativo o cero?"
- **Experto 3 (CTO):** "Requiero pruebas que validen la *lógica de negocio*, no a FastAPI. Si la BD devuelve error por stock negativo, la prueba debe afirmar que la regla de negocio se respeta."

### 2. Self-Refinement Loop
- *Borrador inicial:* Probar todos los endpoints pasándole un string en vez de int.
- *Refinamiento:* Eso prueba la validación Pydantic (framework), no nuestra lógica. Cambiamos el enfoque a probar *lógica de negocio*, como intentar reducir más stock del que existe, lo cual debe fallar por una regla de negocio y no por tipo de dato.

### 3. Red Teaming (Buscando la ruptura)
- Inyectar modificaciones concurrentes (simuladas) y estados de error.
- Enviar IDs malformados, o deltas de stock extremos (`delta = -9999999` en un inventario de 10).

---

## 📝 Proposed Changes

### Archivos de Configuración y Documentación

#### [NEW] [TESTING.md](file:///workspaces/python-hello/TESTING.md)
Documento que detallará cómo ejecutar las pruebas, qué cubre cada suite y justificación de los casos límite elegidos, como pide el CTO en el ticket AUTH-088.

### Batería de Pruebas (Directorio `tests/`)

Se configurará `pytest` y `pytest-cov`.

#### [NEW] [tests/conftest.py](file:///workspaces/python-hello/tests/conftest.py)
Configuración de fixtures, como un cliente de pruebas (`TestClient` de FastAPI) y una inicialización/limpieza de la base de datos en memoria para tener un entorno limpio en cada test.

#### [NEW] [tests/test_inventory_get.py](file:///workspaces/python-hello/tests/test_inventory_get.py)
Pruebas para `GET /inventory` y `GET /inventory/alerts`:
- **Happy Path:** Recuperar lista vacía, recuperar lista con productos; recuperar alertas correctamente filtradas.
- **Edge Case:** Pedir alertas con `threshold=0`.
- **Failure Mode:** (Red teaming) Simular una base de datos corrupta o inaccesible (mock).

#### [NEW] [tests/test_inventory_post.py](file:///workspaces/python-hello/tests/test_inventory_post.py)
Pruebas para `POST /inventory`:
- **Happy Path:** Creación exitosa de producto.
- **Edge Case:** Nombres de producto extremadamente largos, cantidades en cero.
- **Failure Mode:** Intentar añadir un producto con campos faltantes o formato incorrecto (verificar que se rechaza correctamente).

#### [NEW] [tests/test_inventory_patch.py](file:///workspaces/python-hello/tests/test_inventory_patch.py)
Pruebas para `PATCH /inventory/{product_id}`:
- **Happy Path:** Aumentar stock (+5), disminuir stock (-2).
- **Edge Case:** Disminuir stock dejando exactamente 0.
- **Failure Mode:** 
  - Intentar reducir el stock por debajo de 0 (Debe devolver 400 Bad Request).
  - Intentar modificar un ID que no existe (Debe devolver 404 Not Found).

---

## 🚀 Fases de Ejecución

### Fase 1: Preparación del Entorno
- Instalar `pytest`, `pytest-cov` y `httpx`.
- Configurar base de ejecución.

### Fase 2: Aislamiento (El archivo `conftest.py`)
- Crear `tests/conftest.py`.
- Configurar un *fixture* de `TestClient` para aislar pruebas del inventario real.

### Fase 3: Pruebas de "Camino Feliz" (Happy Path)
- Crear `tests/test_inventory_get.py` (listar productos y alertas).
- Crear `tests/test_inventory_post.py` (añadir productos).
- Crear `tests/test_inventory_patch.py` (actualizar stock).

### Fase 4: Pruebas de Límite y Fallo (Edge Cases & Failure Modes)
- Límite exacto de 0 en el inventario.
- Errores HTTP 400 (stock negativo).
- Errores HTTP 404 (producto inexistente).

### Fase 5: Medición de Cobertura y Cierre
- Ejecutar `uv run pytest --cov`.
- Asegurar >70% de cobertura.

---

## 🧪 Verification Plan

### Automated Tests
1. **Ejecución Básica:** 
   ```bash
   uv run pytest
   ```
   *Objetivo: Todos los tests pasan.*

2. **Verificación de Cobertura:** 
   ```bash
   uv run pytest --cov=api --cov-report=term-missing
   ```
   *Objetivo: Alcanzar mínimo un 70% de cobertura en la lógica (como exige el ticket original).*

### Manual Verification
- Revisión manual de `TESTING.md` para comprobar que refleja las pruebas reales, documenta la ejecución y detalla los casos elegidos usando asistencia de IA, de acuerdo con los criterios de evaluación.
