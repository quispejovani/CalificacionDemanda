<<<<<<< HEAD
# EDA — Calificación de demandas de alimentos (Iyotatsiri / SISGESC)

**Estado:** plantilla reproducible; **sin expedientes reales cargados**. No se reportan métricas ni resultados empíricos hasta disponer de un conjunto de datos anonimizado y validado.

## Objetivo
Explorar la calidad y distribución de demandas y resoluciones históricas de alimentos antes de entrenar el clasificador supervisado que apoyará la elaboración de proyectos de calificación argumentados.

## Uso
1. Crear entorno Python y ejecutar `pip install -r requirements.txt`.
2. Asignar identificadores seudónimos y elaborar el CSV usando `data/processed/casos_plantilla.csv` y `data/data_dictionary.csv`.
3. **No incluir PDF originales ni datos personales en GitHub.** La extracción inicial de metadatos puede realizarse localmente con `scripts/inventario_pdfs.py`.
4. Ejecutar `notebooks/01_eda_calificacion_alimentos.ipynb` desde la raíz del repositorio.
5. Revisar los gráficos generados localmente en `reports/figures/`.

## Reglas metodológicas
- La etiqueta `calificacion_validada` procede de la resolución y revisión experta, no de inferencias automáticas del notebook.
- Valores ausentes/ambiguos se registran como vacíos o `NO_DETERMINADO`; no se convierten automáticamente en incumplimientos jurídicos.
- La resolución es **fuente de etiqueta**, no característica predictora: evitar fuga de información al entrenar.
- Dividir futuros conjuntos train/validation/test por expediente/grupo y, de ser posible, por tiempo.
- El EDA no entrena ni aprueba ningún modelo.

## Publicación de rama
```bash
git init
git checkout -b feature/eda-calificacion-alimentos
git add .
git commit -m "EDA inicial de calificación de alimentos"
git remote add origin https://github.com/TU_USUARIO/iyotatsiri-eda-calificacion-alimentos.git
git push -u origin feature/eda-calificacion-alimentos
```
El enlace que entregarás tendrá formato `https://github.com/TU_USUARIO/iyotatsiri-eda-calificacion-alimentos/tree/feature/eda-calificacion-alimentos` y será real solo después de publicarlo.
=======
# CalificacionDemanda
Proyecto de Calificación de Demanda de los procesos de alimentos

# Esquema
IYOTATSIRI / SISGESC
└── Calificación de Demanda de Alimentos
    │
    ├── 1. Preparación del dataset
    │   ├── Expedientes históricos
    │   ├── Demanda y anexos
    │   ├── Anonimización
    │   └── Etiquetado jurídico
    │
    ├── 2. Entrenamiento previo
    │   ├── OCR
    │   ├── Extracción de características
    │   ├── Clasificación documental
    │   └── Clasificador de calificación
    │
    ├── 3. Evaluación
    │   ├── Train
    │   ├── Validation
    │   ├── Test
    │   ├── Precision / Recall / F1
    │   └── Matriz de confusión
    │
    ├── 4. Validación jurídica
    │   ├── Requisitos procesales
    │   ├── Evidencias encontradas
    │   ├── Reglas jurídicas
    │   └── Revisión de errores
    │
    ├── 5. Documentación
    │   ├── Dataset utilizado
    │   ├── Algoritmo
    │   ├── Parámetros
    │   ├── Métricas
    │   ├── Limitaciones
    │   └── Versión del modelo
    │
    ├── 6. Aprobación
    │
    └── 7. Uso en SISGESC
        └── Demanda nueva
             ↓
            OCR
             ↓
        Análisis documental
             ↓
        Requisitos + evidencia
             ↓
        Reglas jurídicas
             ↓
        Modelo entrenado
             ↓
        PROPUESTA DE CALIFICACIÓN
             ↓
        Revisión humana
>>>>>>> 80cd711231423549a784099d4afcd6c2793ed7de
