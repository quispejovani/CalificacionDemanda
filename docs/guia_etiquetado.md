# Protocolo de etiquetado jurídico

1. Asignar ID seudónimo y asociar demanda con su resolución, conservando originales únicamente en repositorio institucional autorizado.
2. Extraer **solo** información necesaria y minimizar datos personales; verificar el proceso de anonimización antes de publicar.
3. Registrar `ADMISION`, `INADMISIBILIDAD`, `IMPROCEDENCIA` o `OTRA/NO_DETERMINADA` de acuerdo con el acto de calificación efectivamente verificado. No confundir una subsanación posterior con la resolución inicial.
4. Revisar manualmente petitorio, partes, firma y anexos; `NO_DETERMINADO` significa evidencia insuficiente, no incumplimiento.
5. Registrar motivo, fundamento normativo y fecha/versión normativa; evitar reglas jurídicas simplificadas (por ejemplo, ausencia de empleo del demandado no implica automáticamente inadmisibilidad).
6. Etiquetado independiente por dos revisores cuando sea viable; documentar discrepancias y adjudicación por experto.
7. Guardar el historial de cambios de etiquetas y las reglas aplicadas; no entrenar con registros sin validación jurídica.
8. Mantener resoluciones fuera de las variables de entrada del futuro clasificador para evitar filtración de la respuesta.

## Criterios de calidad
Completitud, consistencia temporal, duplicados, proporción de clases, calidad OCR, revisión experta y trazabilidad de cada etiqueta.
