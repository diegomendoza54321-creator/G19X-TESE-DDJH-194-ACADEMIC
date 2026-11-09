# Auditoría Final de Documentación — MotorRevisionLegal

**Fecha:** 2026-11-08  
**Alcance:** Análisis de 5 documentos principales del repositorio  
**Objetivo:** Identificar texto obsoleto, pendientes falsos, tecnologías antiguas, acentos dañados, referencias inconsistentes y conteos incorrectos.

---

## 1. README.md

### 1.1 Acentos dañados (corrupción UTF-8)
| Línea | Texto actual | Corrección |
|-------|--------------|------------|
| 65 | `RevisiÃ³n de cÃ³digo` | `Revisión de código` |
| 65 | `ackend/app/analisis_ia.py` | `backend/app/analisis_ia.py` |
| 67 | `DocumentaciÃ³n` | `Documentación` |
| 75 | `modificaciÃ³n` | `modificación` |

### 1.2 Texto obsoleto / información específica de máquina de desarrollo
| Línea | Problema |
|-------|----------|
| 149-151 | Líneas vacías duplicadas entre descarga de llama-server y ejecutable |
| 153-154 | Referencias a rutas absolutas `D:\llama.cpp\llama-server.exe`, versión `0.7.0-dev (build 11683, commit a8d9a7e1e)`, `D:\Modelos\Phi-3-mini-4k-instruct-q4.gguf`, puerto 9932 — son datos de la máquina de desarrollo, no requisitos generales |
| 289 | Mismo problema: rutas `D:\llama.cpp\...`, `D:\Modelos\...`, pruebas en puerto 9932 |

### 1.3 Conteos de pruebas incorrectos
| Línea | Texto actual | Realidad |
|-------|--------------|----------|
| 263 | `102 pruebas... test_analisis_ia.py 29, test_api.py 10, test_auth.py 17, test_citas.py 28, test_extraccion.py 14, test_historial.py 4` | Conteo real: `test_analisis_ia.py 36, test_api.py 10, test_auth.py 15, test_citas.py 24, test_extraccion.py 14, test_historial.py 4 = 103 (grep)`, pero pytest reporta 109 por parametrización |

### 1.4 Referencias inconsistentes
| Línea | Problema |
|-------|----------|
| 67 | `docs/plan-de-pruebas.md` aparece dos veces en la lista de documentos asistidos por IA |
| 295-299 | Sección "Estructura del proyecto" vacía (solo comillas invertidas) |
| 303-315 | Tabla de documentación lista `docs/guia-instalacion.md` y `docs/manual-usuario.md` que no existen en el repositorio |

---

## 2. docs/MVP.md

### 2.1 Estado del documento obsoleto
| Línea | Texto actual | Realidad |
|-------|--------------|----------|
| 5 | `Estado: En elaboración` | Proyecto es prototipo funcional completo |
| 245-246 | `Ninguna de estas condiciones está cumplida todavía. El estado actual es: documentación en elaboración, implementación no iniciada.` | **FALSO** — Implementación completada: backend, frontend, IA local, historial, variables de entorno, pruebas |
| 249 | `Este documento es un borrador sujeto a revisión y ajuste` | No es borrador; refleja MVP ya implementado |

### 2.2 Pendientes falsos (marcados como pendientes pero ya implementados)
| Línea | Pendiente declarado | Implementación real |
|-------|---------------------|---------------------|
| 29-30 | Mecanismo técnico de autenticación + creación/administración de cuentas | JWT + `crear_usuario.py` funcionando |
| 45 | Tamaño máximo de archivo | No implementado (sigue pendiente real) |
| 77 | Criterios de revisión base/condicionales "sujetos a revisión... (pendiente)" | `backend/app/criterios.json` existe y se usa en producción |
| 100 | Motor de BD, campos, política de conservación "pendientes de definir" | SQLite implementado en `auth.py` y `historial.py`; campos definidos; política pendiente |
| 171 | Selección proveedor IA "Define la arquitectura... pendiente" | `llama-server` local ya elegido e integrado |
| 175 | Motor de BD "pendiente" | SQLite implementado |
| 176 | Campos exactos y política "pendientes" | Parcialmente implementado (campos sí, política no) |
| 178 | Tamaño máximo archivo "pendiente" | Correcto — sigue pendiente |

### 2.3 Referencias inconsistentes
| Línea | Problema |
|-------|----------|
| 6 | Enlace relativo `[`PRD.md`](PRD.md)` y `[`requisitos.md`](requisitos.md)` — funcionan solo desde `docs/` |
| 165 | Tabla "Decisiones pendientes" incluye ítems ya resueltos (autenticación, BD, proveedor IA) sin marcar como resueltos |

---

## 3. docs/arquitectura.md

### 3.1 Estado del documento obsoleto
| Línea | Texto actual | Realidad |
|-------|--------------|----------|
| 5 | `Estado: Propuesta sujeta a validación — el código no existe todavía` | **FALSO** — Código completo existe y funciona |
| 270 | `Este documento es una propuesta inicial sujeta a revisión` | No es propuesta; arquitectura implementada |

### 3.2 Tecnologías marcadas como "candidatas/pendientes" pero ya confirmadas e implementadas
| Componente | Líneas | Estado documentado | Estado real |
|------------|--------|-------------------|-------------|
| Frontend | 16-17, 80-81 | `React + TypeScript (candidato)`, `Pendiente de confirmar` | **Confirmado e implementado** |
| Estilos | 17, 80 | `Tailwind CSS (candidato)`, `Pendiente de confirmar` | **Confirmado e implementado** |
| Backend | 34, 99-100 | `Python + FastAPI (candidato)`, `Pendiente de confirmar` | **Confirmado e implementado** |
| Base de datos | 52-53, 63-66, 135-136, 143 | `*(pendiente)`, `Candidato: PostgreSQL u otro`, `Pendiente de definir` | **SQLite implementado** |
| Servicio IA | 53, 62-66, 120-121, 129 | `*(pendiente)`, `Candidato: API de OpenAI u otra`, `Pendiente de validar` | **llama-server local implementado** |
| Autenticación | 105, 230 | `Pendiente de definir` | **JWT implementado** |
| Extracción PDF | 227 | `Pendiente de evaluar y comparar` | **pypdf + python-docx implementados** |
| Pruebas backend | 233 | `Pendiente de confirmar` | **pytest implementado y pasando (109 tests)** |

### 3.3 Pendientes falsos en "Aspectos pendientes de definir" (líneas 258-267)
| Ítem | Línea | Estado real |
|------|-------|-------------|
| Proveedor IA | 258 | **Resuelto**: llama-server local |
| Autenticación | 259 | **Resuelto**: JWT |
| Cuentas autorizadas | 260 | **Resuelto**: `crear_usuario.py` |
| Motor BD | 261 | **Resuelto**: SQLite |
| Campos historial | 262 | **Parcial**: campos definidos, política pendiente |
| Política docs | 263 | Pendiente real |
| Despliegue | 264 | Pendiente real (entorno demo) |
| Errores IA | 265 | **Resuelto**: retry 503 en frontend + 503 en backend |
| Tamaño máximo | 266 | Pendiente real |

### 3.4 Referencias inconsistentes
| Línea | Problema |
|-------|----------|
| 72 | "IA externa queda pendiente de proveedor" — contradictorio con uso de llama-server local |
| 129 | Restricción "no enviar a servicios externos" — correcta, pero el documento no refleja que se usa IA local |

---

## 4. docs/PRD.md

### 4.1 Estado del documento obsoleto
| Línea | Texto actual | Realidad |
|-------|--------------|----------|
| 5 | `Estado: En elaboración` | Producto funcional implementado |

### 4.2 Pendientes falsos
| Línea | Pendiente declarado | Implementación real |
|-------|---------------------|---------------------|
| 19 | "Creación y administración de cuentas está pendiente de definir" | `backend/crear_usuario.py` funcional |
| 61 | "Campos exactos que se guardarán y política de conservación están pendientes de definir" | Campos implementados en `historial.py`; política pendiente |
| 109 | "Mecanismo técnico de autenticación... está pendiente de definir" | JWT implementado en `auth.py` |
| 121 | "Tamaño máximo del archivo se define durante el desarrollo. *(pendiente)*" | Correcto — pendiente real |
| 182 | "Motor de base de datos: SQLite (implementado...)" | **Correcto** — única mención precisa |
| 222 | "Validar la API de IA: privacidad, costo... Pendiente" | **Resuelto**: llama-server local (sin costo, privacidad total) |
| 223 | "Mecanismo técnico de autenticación... el mecanismo de implementación no" | **Resuelto**: JWT |
| 224 | "Creación y administración de cuentas... Pendiente" | **Resuelto**: `crear_usuario.py` |
| 226 | "Datos exactos que guardará el historial y política de conservación" | Parcial: datos sí, política no |
| 227 | "Política de almacenamiento y eliminación de documentos cargados" | Pendiente real |
| 228 | "Definir y ajustar internamente la lista de criterios... (pendiente)" | **Resuelto**: `criterios.json` en uso |
| 229 | "Tamaño máximo de archivo aceptado" | Pendiente real |
| 230 | "Estrategia de despliegue" | Pendiente real (entorno demo) |

### 4.3 Referencias inconsistentes
| Línea | Problema |
|-------|----------|
| 61 | Dice "motor de base de datos es SQLite (implementado en backend/app/auth.py y backend/app/historial.py)" — correcto, pero contradictorio con líneas 19, 109, 223-224 que dicen que está pendiente |
| 225 | Checkbox `[x] Motor de base de datos: SQLite (implementado...)` — correcto, pero el resto de la lista no se actualizó |

---

## 5. docs/requisitos.md

### 5.1 Estado del documento obsoleto
| Línea | Texto actual | Realidad |
|-------|--------------|----------|
| 5 | `Estado: En elaboración` | Requisitos implementados y validados |
| 212 | `Este documento es un borrador inicial` | No es borrador; requisitos cubiertos por implementación |

### 5.2 Pendientes falsos
| Línea | Requisito | Estado real |
|-------|-----------|-------------|
| 18-19 | RF-00.4 y RF-00.5: autenticación y cuentas "pendientes de definir" | **Implementados**: JWT + `crear_usuario.py` |
| 48 | "Solo RF-03: RF-04 se implementa con criterios provisionales definidos internamente" | Confuso: RF-04 **sí está implementado** con criterios en `criterios.json` |
| 116 | RF-08.6: "Motor de BD, campos, política... pendientes de definir" | Parcial: motor y campos **implementados** (SQLite), política pendiente |
| 155 | RNF-04.1: "Convenciones de estilo... pendiente de definir" | Proyecto tiene convenciones (PEP 8, ESLint, Prettier) |
| 157 | RNF-04.3: "Lista de verificación modificable sin cambiar código... pendiente de diseño" | **Implementado**: `criterios.json` externo |

### 5.3 Referencias inconsistentes
| Línea | Problema |
|-------|----------|
| 48 | Nota dice "Solo RF-03: RF-04 se implementa con criterios provisionales" — sugiere que RF-04 no está completo, pero sí lo está |
| 116 | RF-08.6 repite "pendiente de definir" para motor y campos que ya existen |

---

## 6. Resumen Consolidado de Conteos de Pruebas

| Fuente | test_analisis_ia | test_api | test_auth | test_citas | test_extraccion | test_historial | Total |
|--------|------------------|----------|-----------|------------|-----------------|----------------|-------|
| README.md (línea 263) | 29 | 10 | 17 | 28 | 14 | 4 | **102** |
| plan-de-pruebas.md | — | — | — | — | — | — | **101** |
| manual-tecnico.md | — | — | — | — | — | — | **102** |
| **Realidad (grep ^def test_)** | **36** | **10** | **15** | **24** | **14** | **4** | **103** |

**Discrepancias:**
- `test_analisis_ia.py`: documentados 29 vs reales 36 (+7 por archivo; 6 más por parametrización en pytest)
- `test_auth.py`: documentados 17 vs reales 15 (-2 por archivo; +3 por parametrización en pytest)
- `test_citas.py`: documentados 28 vs reales 24 (-4 por archivo; +6 por parametrización en pytest)
- Total documentados: 102 vs reales 103

---

## 7. Acciones Recomendadas (solo análisis — sin modificar archivos)

1. **README.md**: Corregir acentos dañados (líneas 65, 67, 75); eliminar/actualizar rutas de máquina de desarrollo (líneas 153-154, 289); corregir conteo de pruebas a 103 con distribución real; completar sección "Estructura del proyecto" (líneas 295-299); eliminar docs inexistentes de tabla (guia-instalacion.md, manual-usuario.md).

2. **MVP.md**: Cambiar estado a "Implementado/Validado"; eliminar nota falsa de "implementación no iniciada" (líneas 245-246); marcar decisiones resueltas en tabla (líneas 169-180); actualizar pendientes reales vs resueltos.

3. **arquitectura.md**: Cambiar estado a "Implementada"; quitar "(candidato)" y "Pendiente de confirmar" de todas las tecnologías; actualizar BD a SQLite, IA a llama-server local; marcar aspectos resueltos en sección 6.

4. **PRD.md**: Cambiar estado a "Validado"; sincronizar pendientes con realidad (líneas 19, 61, 109, 222-230); solo tamaño máximo, política conservación, política docs, despliegue siguen pendientes.

5. **requisitos.md**: Cambiar estado a "Validado"; corregir RF-00.4/00.5, RF-08.6, RNF-04.1/04.3; aclarar nota RF-04 (línea 48).

6. **Conteos de pruebas**: Unificar a **109 pruebas** (pytest conta casos parametrizados individualmente) en README, plan-de-pruebas.md, manual-tecnico.md.

---

*Fin de auditoría. Este documento es solo análisis; no modifica ningún archivo del repositorio.*