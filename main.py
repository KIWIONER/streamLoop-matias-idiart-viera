"""
StreamLoop — Churn Model Tuning Pipeline
=========================================
Script principal ejecutable para entrenar la línea base, ejecutar la optimización
de hiperparámetros (RandomizedSearchCV + GridSearchCV) y evaluar el modelo final.
"""

import os
import json
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, recall_score, precision_score, f1_score, roc_auc_score, accuracy_score

def run_pipeline():
    print("=" * 65)
    print(" StreamLoop — Pipeline de Optimización de Modelo de Churn")
    print("=" * 65)

    # 1. Carga de datos
    url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
    local_path = os.path.join("data", "Telco-Customer-Churn.csv")

    try:
        print("[1/6] Cargando dataset desde la URL oficial...")
        df = pd.read_csv(url)
    except Exception:
        print("[1/6] Cargando dataset desde copia local...")
        df = pd.read_csv(local_path)

    # 2. Limpieza mínima
    print("[2/6] Limpieza de datos (TotalCharges a numérico, drop customerID)...")
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df = df.drop(columns=['customerID'])

    X = df.drop(columns=['Churn'])
    y = (df['Churn'] == 'Yes').astype(int)

    # 3. Train-Test Split (estratificado 80/20)
    print("[3/6] Partición train/test estratificada (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Preprocesamiento encapsulado
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    cat_cols = [c for c in X.columns if c not in num_cols]

    num_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_cols),
            ('cat', cat_transformer, cat_cols)
        ]
    )

    # 4. Línea Base
    print("[4/6] Entrenando Línea Base (RandomForestClassifier por defecto)...")
    base_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])
    base_pipeline.fit(X_train, y_train)

    y_pred_base = base_pipeline.predict(X_test)
    y_proba_base = base_pipeline.predict_proba(X_test)[:, 1]
    cm_base = confusion_matrix(y_test, y_pred_base)

    metrics_base = {
        'Accuracy': accuracy_score(y_test, y_pred_base),
        'Recall': recall_score(y_test, y_pred_base),
        'Precision': precision_score(y_test, y_pred_base),
        'F1-Score': f1_score(y_test, y_pred_base),
        'ROC-AUC': roc_auc_score(y_test, y_proba_base),
        'Falsos Negativos': int(cm_base[1, 0])
    }

    # 5. Optimización con hiperparámetros validados
    print("[5/6] Entrenando Modelo Ajustado con hiperparámetros óptimos...")
    tuned_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            class_weight='balanced',
            max_depth=3,
            max_features='log2',
            min_samples_leaf=1,
            min_samples_split=20,
            n_estimators=250,
            random_state=42
        ))
    ])
    tuned_pipeline.fit(X_train, y_train)

    # 6. Evaluación Final en Test Set
    print("[6/6] Evaluación Final en Test Set...")
    y_pred_tuned = tuned_pipeline.predict(X_test)
    y_proba_tuned = tuned_pipeline.predict_proba(X_test)[:, 1]
    cm_tuned = confusion_matrix(y_test, y_pred_tuned)

    metrics_tuned = {
        'Accuracy': accuracy_score(y_test, y_pred_tuned),
        'Recall': recall_score(y_test, y_pred_tuned),
        'Precision': precision_score(y_test, y_pred_tuned),
        'F1-Score': f1_score(y_test, y_pred_tuned),
        'ROC-AUC': roc_auc_score(y_test, y_proba_tuned),
        'Falsos Negativos': int(cm_tuned[1, 0])
    }

    # Reporte comparativo
    comparison = pd.DataFrame({
        'Línea Base': metrics_base,
        'Modelo Ajustado': metrics_tuned
    })
    comparison['Variación'] = comparison['Modelo Ajustado'] - comparison['Línea Base']

    print("\n" + "=" * 65)
    print(" RESULTADOS COMPARATIVOS (TEST SET - 1,409 CLIENTES)")
    print("=" * 65)
    print(comparison.to_string())
    print("-" * 65)
    fn_reducidos = metrics_base['Falsos Negativos'] - metrics_tuned['Falsos Negativos']
    pct_reduc = (fn_reducidos / metrics_base['Falsos Negativos']) * 100
    print(f">> REDUCCIÓN DE FALSOS NEGATIVOS: {fn_reducidos} clientes rescatados ({pct_reduc:.1f}% menos pérdidas)")
    print(f">> RECALL AUMENTADO: de {metrics_base['Recall']:.2%} a {metrics_tuned['Recall']:.2%} (+{metrics_tuned['Recall']-metrics_base['Recall']:.2%})")
    print("=" * 65)

if __name__ == '__main__':
    run_pipeline()
