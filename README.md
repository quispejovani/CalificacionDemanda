# Proyección de Auto de Calificación de Demandas en la especialidad y subespecialidad de Familia Civil en Materia de Alimentos

**Proyecto de tesis:** CalificacionDemanda  
**Estado:** Investigación y desarrollo experimental — documento metodológico sujeto a validación.  
**Alcance:** Demandas judiciales de alimentos; se excluyen solicitudes y procedimientos de conciliación.

## 1. Resumen del proyecto

CalificacionDemanda investiga el desarrollo de un sistema híbrido de inteligencia artificial para **apoyar la elaboración de proyectos de autos de calificación de demandas judiciales de alimentos**. La propuesta combina extracción y organización documental, identificación de requisitos procesales, aprendizaje automático supervisado y aplicación explícita de reglas jurídicas. Su producto esperado es un **proyecto de auto fundamentado y trazable**, sujeto a revisión y aprobación de la autoridad jurisdiccional competente; el sistema NO SUSTITUYE la decisión judicial.

<<<<<<< HEAD
## Reglas metodológicas
- La etiqueta `calificacion_validada` procede de la resolución y revisión experta, no de inferencias automáticas del notebook.
- Valores ausentes/ambiguos se registran como vacíos o `NO_DETERMINADO`; no se convierten automáticamente en incumplimientos jurídicos.
- La resolución es **fuente de etiqueta**, no característica predictora: evitar fuga de información al entrenar.
- Dividir futuros conjuntos train/validation/test por expediente/grupo y, de ser posible, por tiempo.
- El EDA no entrena ni aprueba ningún modelo.
=======
# CalificacionDemanda
Proyecto de Calificación de Demanda de los procesos de alimentos
=======
## 2. Problema de investigación

**Problema general (PG).** ¿En qué medida un sistema de inteligencia artificial híbrido mejora la calidad y eficiencia de la proyección de autos de calificación de demandas de alimentos en la especialidad y subespecialidad de Familia Civil?
>>>>>>> feature/importancia-variables-matriz

**Problemas específicos.**

- **PE1.** ¿Cómo identificar y estructurar la información jurídica relevante de las demandas y sus anexos?
- **PE2.** ¿Qué características documentales, procesales y jurídicas contribuyen a la evaluación de las demandas de alimentos?
- **PE3.** ¿Qué desempeño alcanza un modelo supervisado al proponer la categoría de calificación judicial?
- **PE4.** ¿Cómo incorporar reglas jurídicas para generar proyectos de auto debidamente fundamentados?
- **PE5.** ¿En qué medida el sistema mejora la calidad y eficiencia de la elaboración de proyectos de auto?

## 3. Objetivos

**Objetivo general (OG).** Desarrollar y evaluar un sistema de inteligencia artificial híbrido para apoyar la proyección de autos de calificación de demandas de alimentos, mediante análisis documental, verificación de requisitos procesales y generación de propuestas jurídicamente fundamentadas.

**Objetivos específicos.**

- **OE1.** Implementar un procedimiento de extracción, clasificación documental y estructuración de información jurídica.
- **OE2.** Identificar, construir y evaluar características relevantes mediante ingeniería e importancia de variables.
- **OE3.** Desarrollar y comparar modelos supervisados para apoyar la identificación de admisibilidad, inadmisibilidad e improcedencia.
- **OE4.** Diseñar e implementar un mecanismo de aplicación de reglas jurídicas y generación de proyectos de auto con evidencia verificable.
- **OE5.** Evaluar la calidad jurídica, concordancia experta y tiempo de elaboración de los proyectos generados frente a un procedimiento de referencia.

## 4. Hipótesis

**Hipótesis general (HG).** La utilización de un sistema de inteligencia artificial híbrido mejora celeridad procesal, la predictibilidad, consistencia, la trazabilidad y la eficiencia de la proyección de autos de calificación de demandas de alimentos.

**Hipótesis específicas.**

- **HE1.** El procesamiento documental permite obtener información estructurada con niveles medibles de cobertura y exactitud.
- **HE2.** La incorporación de características jurídicamente pertinentes mejora el desempeño del modelo frente a una representación de referencia.
- **HE3.** Una variante supervisada mejora el desempeño respecto del modelo de referencia bajo condiciones de evaluación equivalentes.
- **HE4.** La incorporación de reglas jurídicas mejora la cobertura de requisitos y la trazabilidad de los fundamentos frente a una generación sin reglas explícitas.
- **HE5.** El sistema reduce el tiempo de elaboración sin deteriorar la calidad jurídica de los proyectos.

> Revisar por docente para validar

## 5. Matriz de consistencia

| Problema | Objetivo | Hipótesis | Variables independientes y dependientes | Indicadores |
|---|---|---|---|---|
| **PG:** ¿En qué medida un sistema híbrido mejora la calidad y eficiencia de la proyección de autos de calificación de demandas de alimentos? | **OG:** Desarrollar y evaluar un sistema híbrido para apoyar la proyección de autos de calificación de demanda de alimentos. | **HG:** Mejora la celeridad procesal, consistencia, trazabilidad y eficiencia. | **VI:** Sistema de IA híbrido. **VD:** Celeridad y eficiencia de la proyección de autos. | Concordancia experta; calidad de fundamentación; trazabilidad; tiempo; tasa de errores jurídicos. |
| **PE1:** ¿Cómo identificar y estructurar información relevante de demandas y anexos? | **OE1:** Implementar extracción, clasificación documental y estructuración. | **HE1:** Se obtiene información estructurada con cobertura y exactitud medibles. | **VI1:** Procesamiento documental. **VD1:** Calidad de información extraída. | Cobertura de extracción; precisión de identificación documental; exactitud de campos; documentos revisados. |
| **PE2:** ¿Qué características contribuyen a la evaluación de demandas? | **OE2:** Construir y evaluar características e importancia de variables. | **HE2:** Las características pertinentes mejoran el desempeño frente a una representación de referencia. | **VI2:** Características documentales y jurídicas. **VD2:** Desempeño predictivo. | Importancia por permutación; macro-F1; recall por clase; cambio de desempeño por ablación. |
| **PE3:** ¿Qué desempeño alcanza un clasificador supervisado? | **OE3:** Comparar modelos para admisibilidad, inadmisibilidad e improcedencia. | **HE3:** Una variante mejora el desempeño frente al modelo de referencia. | **VI3:** Configuración del clasificador. **VD3:** Desempeño predictivo. | Macro-F1; recall por clase; matriz de confusión; latencia. |
| **PE4:** ¿Cómo incorporar reglas jurídicas a la generación de proyectos de auto? | **OE4:** Implementar reglas y generación de proyectos con evidencia verificable. | **HE4:** Las reglas mejoran cobertura de requisitos y trazabilidad. | **VI4:** Motor de reglas jurídicas. **VD4:** Fundamentación y trazabilidad. | Cobertura de requisitos; exactitud normativa; correspondencia evidencia-fundamento; errores jurídicos. |
| **PE5:** ¿En qué medida mejora la calidad y eficiencia de los proyectos? | **OE5:** Evaluar calidad, concordancia experta y tiempo frente a referencia. | **HE5:** Disminuye el tiempo sin deteriorar calidad jurídica. | **VI5:** Modalidad de elaboración. **VD5:** Calidad y eficiencia. | Tiempo por proyecto; concordancia experta; correcciones sustanciales; aceptación tras revisión. |

## 6. Variables y operacionalización

### Variable independiente general

**Sistema de inteligencia artificial híbrido para la proyección de autos de calificación.**

| Dimensión | Indicadores operativos | Instrumentos |
|---|---|---|
| Procesamiento documental | Cobertura OCR; identificación de tipos documentales; exactitud de campos | PyMuPDF, Tesseract, revisión humana |
| Ingeniería de características | Variables construidas; estabilidad; importancia | Python y scikit-learn |
| Aprendizaje supervisado | Configuración del modelo; rendimiento; latencia | Experimentos reproducibles |
| Reglas jurídicas | Requisitos codificados; cobertura; verificabilidad | Motor de reglas y revisión experta |
| Generación del proyecto | Estructura del auto; evidencia asociada; trazabilidad | Generador y registros de auditoría |

### Variable dependiente general

**Calidad y eficiencia de la proyección de autos de calificación de demandas de alimentos.**

| Dimensión | Indicador | Forma de evaluación |
|---|---|---|
| Corrección jurídica | Concordancia con evaluación experta | Revisión de casos con criterio de referencia validado |
| Fundamentación | Exactitud normativa y pertinencia de fundamentos | Rúbrica jurídica |
| Integridad | Requisitos examinados correctamente | Lista de verificación |
| Trazabilidad | Fundamentos vinculados con evidencia | Auditoría de documentos y reglas |
| Eficiencia | Tiempo de elaboración por proyecto | Medición de tiempos en tareas comparables |
| Consistencia | Variabilidad en casos equivalentes | Escenarios controlados y revisión experta |

**Distinción metodológica:** en el clasificador supervisado, la *etiqueta objetivo* es `ADMISIBLE`, `INADMISIBLE` o `IMPROCEDENTE`; la **variable dependiente de la tesis** es más amplia y también comprende calidad jurídica, fundamentación y eficiencia.

## 7. Metodología y diseño experimental

Investigación aplicada y de desarrollo tecnológico, con evaluación cuantitativa y revisión jurídica experta. El diseño definitivo, los criterios de aceptación y el procedimiento de referencia deberán acordarse con el asesor y los especialistas.

**Flujo previsto:**

1. Inventariar expedientes, demandas y anexos disponibles antes de la decisión judicial.
2. Extraer texto con PyMuPDF y OCR cuando corresponda.
3. Clasificar documentos y regiones de páginas, incluyendo carátulas, cargos de ingreso, DNI, actas de nacimiento, constancias, boletas, facturas y fotografías.
4. Registrar uno o varios alimentistas por demanda y asociarles los documentos pertinentes.
5. Anonimizar datos personales y validar la trazabilidad documental.
6. Construir características textuales, documentales y jurídicas sin fuga de información.
7. Comparar un modelo de referencia y variantes, manteniendo protocolos de evaluación comunes.
8. Aplicar reglas jurídicas verificables y generar un proyecto de auto con fundamentos y parte resolutiva.
9. Evaluar concordancia experta, corrección jurídica, trazabilidad y tiempo de elaboración.

**Prevención de fuga de información:** los autos de calificación y los documentos producidos después de la presentación no se utilizarán como predictores. La fecha de disponibilidad de cada documento debe verificarse. Las decisiones judiciales podrán utilizarse como etiquetas, previa validación independiente.

**Seguridad:** no publicar expedientes, imágenes de DNI, datos identificativos, textos OCR sin anonimizar ni datasets sensibles. Los documentos originales permanecerán en almacenamiento local protegido.

## 8. Estado del conjunto de datos

Resultados de la revisión local informados hasta el momento:

| Indicador | Estado |
|---|---:|
| Casos judiciales de alimentos validados | 10 |
| PDF de demandas y complementos | 13 |
| Páginas inventariadas | 141 |
| Etiquetas `ADMISIBLE` | 9 |
| Etiquetas `INADMISIBLE` | 1 |
| Etiquetas `IMPROCEDENTE` | 0 |
| Caso de conciliación identificado y excluido | 1 |

**Mejorar la muestra**

## 9. Importancia de variables — siguiente sprint

**Propósito:** analizar qué características disponibles al momento de la presentación contribuyen a la predicción, sin confundir asociación estadística con relevancia jurídica o causalidad.

**Características candidatas:** presencia de petitorio, hechos y fundamentos; identificación de requisitos; número de alimentistas; presencia y asociación de actas de nacimiento; constancias; anexos documentales; y calidad de extracción.

**Diseño previsto:** representación de referencia frente a una variante con características documentales y jurídicas, comparación por macro-F1 y recall por clase, análisis de ablación e importancia por permutación. Estas comparaciones quedarán condicionadas a disponer de un corpus suficientemente amplio y una partición válida.