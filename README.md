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
