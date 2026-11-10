# StreamLoop — Ajustando el Modelo de Cancelación (Churn)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-orange.svg)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Optimizado-brightgreen.svg)]()

Repositorio oficial del proyecto de predicción de abandono (*churn*) para la plataforma de streaming **StreamLoop**. En esta iteración se reemplazó la versión por defecto de `.fit()` mediante un proceso sistemático de optimización de hiperparámetros (*coarse-to-fine search*) con validación cruzada estratificada, priorizando el impacto financiero del negocio.

---

## 🎯 El Desafío del Negocio
StreamLoop pierde sustancialmente más ingresos por cada cliente que cancela su suscripción sin ser detectado (**Falso Negativo**), que por el costo operativo marginal de ofrecer una promoción o beneficio de retención a un cliente que no planeaba cancelar (**Falso Positivo**).

Por ello, se descartó el *accuracy* como métrica directriz y se diseñó la optimización orientada a **maximizar el Recall** sobre la clase positiva (`Churn = Yes`), manteniendo estricto control sobre la estabilidad del modelo entre folds de validación.

---

## 📊 Resultados Destacados (Conjunto de Prueba - 1,409 Clientes)

| Métrica | Línea Base (Default) | Modelo Ajustado (Tuned) | Impacto de Negocio |
| :--- | :---: | :---: | :---: |
| **Recall (Sensibilidad Churn)** | **49.20%** | **82.89%** | **+33.69 pp (+68.5%)** 🚀 |
| **Falsos Negativos (Fugas inadvertidas)** | **190 clientes** | **64 clientes** | **-126 clientes (-66.3%)** 📉 |
| **Verdaderos Positivos (Detectados)** | 184 clientes | 310 clientes | +126 clientes (+68.5%) 📈 |
| **F1-Score** | 54.93% | **60.61%** | +5.68 pp |
| **ROC-AUC** | 82.42% | **83.10%** | +0.68 pp |
| **Accuracy** | 78.57% | 71.40% | Trade-off asumido para maximizar detección |

---

## 🛠️ Arquitectura y Metodología Anti-Leakage

1. **Partición Previa e Intocable:** `train_test_split(stratify=y, test_size=0.2, random_state=42)` ejecutado antes de cualquier imputación o transformación.
2. **Pipeline Hermético:**
   * Variables numéricas (`tenure`, `MonthlyCharges`, `TotalCharges`): Imputadas con mediana + `StandardScaler`.
   * Variables categóricas: Imputadas con la moda + `OneHotEncoder(drop='first', handle_unknown='ignore')`.
   * Clasificador: `RandomForestClassifier`.
3. **Optimización en Dos Fases:**
   * **Fase 1 (Exploración):** `RandomizedSearchCV` (25 iteraciones, 5-Fold Stratified CV, `scoring='recall'`).
   * **Fase 2 (Refinamiento):** `GridSearchCV` concentrado en la región óptima.
4. **Regla de los Dos Toques:** El test set solo fue evaluado **dos veces en todo el ciclo**:
   * Primer toque: Medición formal de la **Línea Base**.
   * Segundo toque: Medición del **Modelo Final Ajustado**.

---

## 📁 Estructura del Repositorio

```text
streamLoop-matias-idiart-viera/
├── data/
│   ├── Telco-Customer-Churn.csv   <- Dataset oficial de clientes
│   └── tuning_results.json        <- Métricas serializadas completas
├── notebooks/
│   └── streamloop_churn.ipynb     <- Cuaderno Jupyter con flujo visual paso a paso
├── main.py                        <- Script para reproducir el entrenamiento y evaluación
├── tuning_report.md               <- Reporte técnico exhaustivo para el Tech Lead
├── implementation_plan.md         <- Plan de implementación detallado
├── strategy.md                    <- Requerimientos y checklist del reto
├── requirements.txt               <- Dependencias de Python
└── README.md                      <- Este documento
```

---

## 🚀 Cómo Reproducir el Proyecto

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/balsamico4g/streamLoop-matias-idiart-viera.git
cd streamLoop-matias-idiart-viera
pip install -r requirements.txt
```

### 2. Ejecutar el Script Principal
```bash
python main.py
```

### 3. Explorar el Notebook Interactivo
Abre `notebooks/streamloop_churn.ipynb` en tu IDE o ejecuta Jupyter Lab:
```bash
jupyter lab notebooks/streamloop_churn.ipynb
```

---

## 📄 Documentación Técnica de Referencia
* [Reporte Técnico de Optimización (`tuning_report.md`)](tuning_report.md)
* [Plan de Implementación y Evaluación (`implementation_plan.md`)](implementation_plan.md)
* [Estrategia y Checklist del Reto (`strategy.md`)](strategy.md)

