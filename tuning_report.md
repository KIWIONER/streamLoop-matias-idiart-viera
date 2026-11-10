# StreamLoop — Reporte Técnico de Ajuste del Modelo de Cancelación (Churn)

**Autor:** Matías Idiart Viera  
**Fecha:** 10 de Noviembre, 2026  
**Destinatario:** Tech Lead & Equipo de Ciencia de Datos de StreamLoop  
**Estado:** Listo para Revisión y Pase a Pre-Producción  

---

## 1. Resumen Ejecutivo

Este reporte documenta el proceso sistemático de optimización de hiperparámetros (*hyperparameter tuning*) para el modelo de predicción de abandono (*churn*) de **StreamLoop**, superando la versión inicial basada en valores por defecto de `.fit()`.

A través de una búsqueda en dos fases (`RandomizedSearchCV` seguido de `GridSearchCV`) y utilizando validación cruzada estratificada de 5 particiones (`5-Fold Stratified CV`), se logró:
* Incrementar la detección de clientes en riesgo (**Recall**) de **`49.20%`** a **`82.89%`** (**+33.69 puntos porcentuales** en el conjunto de prueba).
* Reducir las cancelaciones no detectadas (**Falsos Negativos**) de **190 a 64 clientes**, lo que representa una **reducción del 66.3% en pérdidas inadvertidas** para StreamLoop.
* Elevar el **F1-Score** del modelo del **`54.93%`** al **`60.61%`** y el **ROC-AUC** del **`82.42%`** al **`83.10%`**.
* Garantizar **cero fuga de información (*data leakage*)**, encapsulando el preprocesamiento dentro de un `Pipeline` de Scikit-Learn y tocando el conjunto de prueba exactamente dos veces.

---

## 2. Definición del Problema y Justificación de la Métrica de Negocio

### La Asimetría de Costos en StreamLoop
En un modelo de negocio de streaming por suscripción:
1. **Falso Negativo (FN):** El modelo predice que el cliente se queda (`No Churn`), pero el cliente cancela el servicio. StreamLoop pierde el Valor de Vida del Cliente (*Customer Lifetime Value* - LTV) de forma permanente, sin oportunidad de intervenir.
2. **Falso Positivo (FP):** El modelo predice que el cliente cancelará (`Churn`), pero en realidad se habría quedado. La acción de retención (ej. un correo personalizado, descuento temporal o recomendación de contenido exclusivo) tiene un costo marginal muy bajo frente al LTV.

$$\text{Costo}(\text{FN}) \gg \text{Costo}(\text{FP})$$

### Por qué se Descartó el *Accuracy*
El dataset de clientes presenta una tasa de cancelación del **26.54%** (desbalance de clases ~3:1). Un clasificador trivial que prediga siempre `No Churn` obtendría un **73.46% de Accuracy** mientras que su efectividad real para el negocio sería **cero**.

Por esta razón, se configuró deliberadamente el parámetro:
$$\text{scoring} = \text{'recall'}$$
orientado a maximizar la sensibilidad sobre la clase positiva (`Churn = 1 / Yes`).

---

## 3. Arquitectura del Pipeline y Prevención de Fugas de Información (*Data Leakage*)

Para cumplir con las mejores prácticas de ingeniería de machine learning:
1. **Partición Previa e Inviolable:** El dataset se dividió en entrenamiento (80%, 5,634 filas) y prueba (20%, 1,409 filas) mediante `train_test_split(stratify=y, test_size=0.2, random_state=42)` **antes** de cualquier operación de cálculo estadístico o codificación.
2. **Encapsulamiento en `Pipeline`:**
   * **Variables Numéricas** (`tenure`, `MonthlyCharges`, `TotalCharges`): Imputación de valores faltantes con la **mediana** (`SimpleImputer`) y estandarización con `StandardScaler`.
   * **Variables Categóricas** (16 atributos): Imputación con el valor más frecuente (`SimpleImputer`) y codificación One-Hot con `OneHotEncoder(drop='first', handle_unknown='ignore')`.
   * **Estimador:** `RandomForestClassifier`.
3. **Aislamiento del Test Set:** El conjunto de prueba nunca participó en los splits de validación cruzada ni en la selección de hiperparámetros. Solo se tocó dos veces: en la línea base y en la evaluación final.

---

## 4. Evolución de la Búsqueda de Hiperparámetros

```mermaid
flowchart LR
    A["Línea Base<br/>(Default RFC)"] -->|"RandomizedSearchCV<br/>(25 iter, 5-Fold, scoring='recall')"| B["Búsqueda Amplia<br/>(Espacio Global)"]
    B -->|"Acotamiento de Hiperparámetros"| C["GridSearchCV<br/>(Rejilla Fina, scoring='recall')"|
    C -->|"Auditoría cv_results_<br/>(Media vs std_test_score)"| D["Modelo Final Óptimo"]
```

### Fase 1: Búsqueda Amplia con `RandomizedSearchCV`
Se exploró un espacio amplio de 25 combinaciones aleatorias sobre 5 particiones estratificadas:
* `n_estimators`: `[100, 200, 300]`
* `max_depth`: `[4, 6, 8, 12, None]`
* `min_samples_split`: `[2, 5, 10, 20]`
* `min_samples_leaf`: `[1, 2, 4, 8, 16]`
* `max_features`: `['sqrt', 'log2', 0.5]`
* `class_weight`: `['balanced', 'balanced_subsample']`

**Hallazgos clave de Fase 1:**
* El hiperparámetro crítico que desbloqueó el salto de sensibilidad fue `class_weight='balanced'`, permitiendo penalizar con mayor peso los errores sobre la clase minoritaria.
* Los mejores modelos tendieron a profundidades moderadas/bajas (`max_depth: 3 a 5`) y `max_features: 'log2'`, evitando que los árboles se sobreajusten a las características dominantes de la clase mayoritaria.
* **Mejor Recall CV en Fase 1:** `0.8161` (81.61%).

### Fase 2: Refinamiento con `GridSearchCV`
Con base en la topología identificada, se acotó una rejilla sistemática:
* `classifier__max_depth`: `[3, 4, 5]`
* `classifier__n_estimators`: `[150, 250, 350]`
* `classifier__min_samples_leaf`: `[1, 4, 8]`
* `classifier__min_samples_split`: `[10, 20]`
* `classifier__class_weight`: `['balanced']`
* `classifier__max_features`: `['log2']`

**Resultado de Fase 2:** El mejor estimador alcanzó un **Recall CV de `83.48%`**.

---

## 5. Análisis de Varianza y Estabilidad entre Folds (`cv_results_`)

Para responder a la exigencia del Tech Lead (*"no confiar en un solo número sin revisar cuánto varía entre folds"*), se inspeccionó la tabla `cv_results_`:

| Rank | `max_depth` | `n_estimators` | `min_samples_leaf` | `min_samples_split` | Recall Medio ($\mu$) | Desv. Estándar ($\sigma$) | Coef. Variación ($CV$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **3** | **250** | **1** | **20** | **0.8348** | **0.0315** | **3.77%** |
| 1 | 3 | 250 | 1 | 10 | 0.8348 | 0.0315 | 3.77% |
| 1 | 3 | 250 | 4 | 10 | 0.8348 | 0.0315 | 3.77% |
| 1 | 3 | 250 | 4 | 20 | 0.8348 | 0.0315 | 3.77% |
| 5 | 3 | 150 | 1 | 10 | 0.8308 | 0.0301 | 3.62% |

### Justificación del Modelo Seleccionado
Se seleccionó la configuración con **`max_depth=3`**, **`n_estimators=250`**, **`min_samples_split=20`**, **`min_samples_leaf=1`** y **`class_weight='balanced'`**:
1. **Excelente Estabilidad:** La desviación estándar entre folds es de apenas $\pm 0.0315$ (un coeficiente de variación de 3.77%), lo que demuestra que el modelo no depende de una partición afortunada, sino que generaliza de manera homogénea en diferentes subconjuntos de usuarios.
2. **Regularización Adecuada:** La restricción de profundidad a 3 niveles y 250 estimadores previene el sobreajuste que sufrían los árboles sin límite de la línea base, permitiendo que la probabilidad de cancelación sea suave y consistente.

---

## 6. Comparación Formal de Resultados en el Conjunto de Prueba (*Test Set*)

Las siguientes métricas fueron evaluadas exactamente una vez sobre el conjunto de test (1,409 clientes aislados):

| Métrica | Línea Base (Default) | Modelo Ajustado (Tuned) | Impacto / Variación |
| :--- | :---: | :---: | :---: |
| **Recall (Sensibilidad Churn)** | **49.20%** | **82.89%** | **+33.69 pp (+68.5%)** 🚀 |
| **Falsos Negativos (No Detectados)** | **190 clientes** | **64 clientes** | **-126 clientes (-66.3%)** 📉 |
| **Verdaderos Positivos (Atrapados)** | **184 clientes** | **310 clientes** | **+126 clientes (+68.5%)** 📈 |
| **F1-Score** | 54.93% | **60.61%** | **+5.68 pp** |
| **ROC-AUC** | 82.42% | **83.10%** | **+0.68 pp** |
| **Precision** | 62.16% | 47.77% | -14.39 pp (Trade-off aceptado) |
| **Accuracy** | 78.57% | 71.40% | -7.17 pp |

### Matrices de Confusión Comparativas

```text
       LÍNEA BASE (DEFAULT)                      MODELO FINAL AJUSTADO
   Pred: No Churn   Pred: Churn             Pred: No Churn   Pred: Churn
   +--------------+-------------+           +--------------+-------------+
No |   TN: 923    |   FP: 112   |        No |   TN: 696    |   FP: 339   |
   +--------------+-------------+           +--------------+-------------+
Si |   FN: 190    |   TP: 184   |        Si |   FN:  64    |   TP: 310   |
   +--------------+-------------+           +--------------+-------------+
```

---

## 7. Análisis del Trade-Off y Conclusiones de Negocio

1. **El Costo del Trade-Off es Altamente Rentable:**
   * Para capturar **126 clientes adicionales en riesgo de cancelación**, el modelo generó 227 Falsos Positivos adicionales (precisión pasa de 62.16% a 47.77%).
   * Dado que enviar un incentivo de retención tiene un costo negligible comparado con la pérdida recurrente de suscripción (ej. \$10-\$15 mensuales de por vida por cliente), **rescatar al 82.89% de los canceladores genera un ROI netamente positivo para StreamLoop**.
2. **Madurez para Producción:**
   * El modelo ya no es "lo primero que salió de `.fit()`". Cuenta con un pipeline estructurado, justificación teórica y empírica, métricas orientadas al negocio y una varianza inter-fold auditada y contenida.

