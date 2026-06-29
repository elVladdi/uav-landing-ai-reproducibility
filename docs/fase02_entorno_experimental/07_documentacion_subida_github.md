# Documentacion de subida del proyecto a GitHub

**Proyecto:** `uav-landing-ai`  
**Repositorio remoto:** <https://github.com/elVladdi/uav-landing-ai>  
**Rama principal:** `main`  
**Commit inicial:** `40e9f96 - Initial UAV landing AI project`  
**Fecha de trabajo:** 26 de abril de 2026  
**Directorio local:** `<REPO_ROOT>`

## Resumen

Este documento registra el proceso realizado para inicializar Git, preparar el primer commit y publicar el proyecto local en GitHub.

## 1. Objetivo

Preparar el directorio local del proyecto para control de versiones con Git y publicarlo en GitHub, evitando subir archivos generados, entornos virtuales, datos locales o salidas de ejecucion.

## 2. Diagnostico inicial

- Se confirmo que el directorio existia y contenia un proyecto Python orientado a UAV/AirSim.
- Se verifico que el proyecto no era todavia un repositorio Git.
- La estructura principal incluia `src`, `configs`, `data`, `docs`, `experiments`, `outputs` y `.venv`.
- Se identificaron carpetas generadas o locales que no debian publicarse.

## 3. Preparacion del repositorio

Se creo un archivo `.gitignore` para separar el codigo fuente de los archivos locales o generados durante el uso del proyecto.

Elementos excluidos:

- **Entorno virtual:** `.venv`, `venv` y `env`. Motivo: dependencias locales.
- **Cache Python:** `__pycache__` y `*.pyc`. Motivo: archivos generados.
- **Datos locales:** `data/raw` y `data/logs`. Motivo: datasets o logs locales.
- **Salidas:** `outputs` y `src/perception/outputs`. Motivo: resultados de ejecucion.
- **Secretos:** `.env`, `*.key` y `*.pem`. Motivo: credenciales o llaves.

## 4. Archivos incluidos

El primer commit incluyo el archivo `.gitignore`, los modulos de codigo dentro de `src` y marcadores `.gitkeep` para conservar las carpetas vacias `configs` y `docs`.

- `src/connection`: cliente AirSim y prueba de conexion.
- `src/control`: comandos y pruebas iniciales de control.
- `src/logging`: registro de ejecuciones.
- `src/perception`: pruebas de camara/percepcion.
- `src/utils`: constantes y prueba de estado.

## 5. Comandos ejecutados

Los comandos principales usados para inicializar y publicar el proyecto fueron:

```powershell
git init
git branch -M main
git remote add origin https://github.com/elVladdi/uav-landing-ai.git
git add .
git commit -m "Initial UAV landing AI project"
git push -u origin main
```

## 6. Resultado final

El proyecto quedo publicado correctamente en GitHub. La rama local `main` quedo enlazada con `origin/main` y el estado final del repositorio local quedo limpio.

- **Remoto:** `origin` configurado hacia GitHub.
- **Rama subida:** `main -> origin/main`.
- **Commit publicado:** `40e9f96`.
- **Estado local:** sin cambios pendientes.

## 7. Recomendaciones

- Mantener `.venv`, `outputs` y `data/raw` fuera de Git.
- Agregar y mantener actualizado un `README.md` con descripcion, instalacion, ejecucion y dependencias.
- Usar commits pequenos y descriptivos conforme avance la tesis.
- Revisar `git status` y `git diff` antes de subir nuevos cambios.

## 8. Historial posterior de actualizaciones del repositorio

Despues de la publicacion inicial, el repositorio continuo evolucionando por fases. La siguiente tabla resume las actualizaciones principales realizadas sobre la rama `main`.

| Commit | Descripcion | Alcance principal |
| --- | --- | --- |
| `7af71bb` | `Add PX4 AirSim setup files` | Se agregaron configuraciones, documentacion y cliente inicial para validar PX4 + AirSim mediante MAVSDK/MAVLink. |
| `9c78604` | `Add phase 02 documentation and config` | Se incorporo README, configuracion experimental, documentacion de Fase 02 y notas de instalacion/validacion. |
| `9227adc` | `Reorganize phase 02 documentation` | Se reorganizo la documentacion de Fase 02 en `docs/fase02_entorno_experimental/` y se estructuro en archivos numerados. |
| `a78d758` | `Ignore local Python scripts` | Se retiro del repositorio el versionado de scripts Python locales dentro de `scripts/` y se agrego la regla correspondiente en `.gitignore`. |
| `f96dd83` | `Add phase 03 perception module` | Se agrego el modulo de percepcion visual, configuracion HSV, pipeline offline/en vivo y documentacion de Fase 03. |
| `17660c4` | `Document and validate phase 03 perception` | Se documentaron resultados, manuales, bitacora, diagnostico de camaras y validacion positiva/repetible del detector visual. |
| `aa8442c` | `Add phase 04 autopilot integration` | Se agrego la configuracion de control, wrappers PX4/MAVSDK, control visual, maquina de estados, logger experimental y documentacion de Fase 04. |
| `3719895` | `Update 09_manual_arranque_entorno_simulado.md` | Se actualizo documentacion operativa relacionada con el arranque y validacion del entorno simulado. |
| `979f1ea` | `Update 09_manual_arranque_entorno_simulado.md` | Se incorporaron ajustes adicionales al manual de arranque del entorno simulado para mejorar la reproducibilidad. |
| `ca7180a` | `Add fiducial marker and offboard diagnostics` | Se agrego soporte para marcador fiduciario/ArUco, diagnosticos Offboard, scripts MAVLink/PX4 adicionales, ajustes de percepcion/control y nueva documentacion de Fase 04. |
| `09c2b35` | `Update repository history for fiducial marker work` | Se actualizo el historial del repositorio para reflejar el avance relacionado con marcador fiduciario, diagnosticos Offboard y documentacion tecnica. |

### Estado actual documentado

Al cierre de esta actualizacion, el ultimo commit sincronizado con GitHub es:

```text
09c2b35 Update repository history for fiducial marker work
```

El repositorio mantiene la rama principal `main` enlazada con `origin/main` y se usa como respaldo versionado del avance tecnico de la tesis.

## 9. Actualizacion verificada para publicar: estado del arte y control activo MAVLink

**Fecha de verificacion:** 3 de mayo de 2026  
**Rama:** `main`  
**Base sincronizada:** `09c2b35 - Update repository history for fiducial marker work`

### Resumen de la tanda

Esta actualizacion integra dos bloques de trabajo:

1. Publicacion del estado del arte dentro del repositorio para que pueda leerse directamente desde GitHub.
2. Consolidacion de la subfase de control activo por MAVLink directo, incorporando diagnosticos, documentacion, manejo de modo residual y scripts auxiliares para P04-V02C/P04-V03B.

### Cambios verificados

Se reviso el arbol de trabajo con `git status --short --branch`, `git diff --stat`, lectura de diffs por grupo, verificacion de enlaces Markdown y parseo AST de los scripts Python modificados o nuevos.

Archivos nuevos principales:

- `docs/README.md`: indice general de documentacion del proyecto.
- `docs/estado_del_arte/README.md`: indice de la carpeta academica.
- `docs/estado_del_arte/01_estado_del_arte_uav_vision_ia.md`: version Markdown navegable del estado del arte con citas y referencias APA7.
- `docs/estado_del_arte/02_mapa_literatura_y_alineacion.md`: mapa de literatura, vacio de investigacion y alineacion con la implementacion.
- `docs/fase04_integracion_autopiloto/12_justificacion_control_activo_mavlink.md`: sustento tecnico-academico para evaluar MAVLink directo como ruta de control activo.
- `src/control/run_mavlink_direct_hover_test.py`: prueba P04-V03B para hover minimo por MAVLink directo con UAV ya elevado.
- `src/control/run_mavlink_mode_recovery.py`: helper para recuperar PX4 desde modos residuales `OFFBOARD`/`LAND`.

Archivos modificados principales:

- `README.md`: agrega enlaces al estado del arte, indice de `docs/estado_del_arte/`, nuevos scripts de control y actualiza el enfoque MAVSDK/MAVLink.
- `docs/fase04_integracion_autopiloto/03_protocolo_validacion.md`: incorpora P04-V03B y criterios de aceptacion para hover MAVLink directo.
- `docs/fase04_integracion_autopiloto/04_resultados_validacion.md`: registra resultados P04-V02C, avance parcial P04-V03B y estado residual `OFFBOARD`.
- `docs/fase04_integracion_autopiloto/05_known_issues.md`: agrega KI-0414 a KI-0418 sobre empaquetado PX4, decodificacion de modo, hover MAVLink y recuperacion.
- `docs/fase04_integracion_autopiloto/07_manual_operacion_control_visual.md`: documenta la operacion por MAVLink directo y recuperacion de modo.
- `docs/fase04_integracion_autopiloto/11_subfase_control_activo_alternativas.md`: selecciona provisionalmente MAVLink directo como siguiente ruta tecnica.
- `src/control/px4_offboard_control.py`: intenta recuperacion desde `LAND` u `OFFBOARD` antes de armar.
- `src/control/run_mavlink_direct_offboard_diagnostic.py`: corrige empaquetado de modo PX4, registra heartbeat crudo y sostiene setpoints despues de solicitar `OFFBOARD`.
- `src/control/run_px4_land.py`: agrega recuperacion de modo residual y mensaje operativo para `run_mavlink_mode_recovery.py`.

### Resultado tecnico documentado

- P04-V02C quedo validado como ruta viable de setpoints por MAVLink directo en la corrida `phase04_20260502_203009_822c9921`, con `post_mode=OFFBOARD`, `px4_main_mode=6` y `MAV_RESULT_ACCEPTED`.
- P04-V03B quedo como avance parcial en `phase04_20260502_204145_87918081`: PX4 acepto `OFFBOARD`, pero la confirmacion llego tarde y no se registraron muestras sostenidas de hover. Debe repetirse con la espera corregida.
- Se agrego recuperacion de modo para evitar que PX4 quede desarmado en tierra pero aun reportando `OFFBOARD`, condicion que provoca rechazo de armado posterior.

### Verificaciones realizadas

- Los enlaces Markdown principales del `README.md`, `docs/README.md` y `docs/estado_del_arte/README.md` resuelven correctamente.
- Los documentos Markdown academicos no presentan mojibake ni signos `?` por problemas de codificacion UTF-8.
- Los scripts `px4_offboard_control.py`, `run_mavlink_direct_offboard_diagnostic.py`, `run_px4_land.py`, `run_mavlink_direct_hover_test.py` y `run_mavlink_mode_recovery.py` pasan parseo AST con Python.
- No se ejecutaron pruebas de vuelo en esta verificacion; P04-V03B queda pendiente de repeticion operativa con AirSimNH + PX4 SITL activos.

### Commit recomendado

Mensaje sugerido para publicar esta tanda:

```text
Publish state of art and MAVLink control updates
```

Comandos sugeridos:

```powershell
git add README.md docs/README.md docs/estado_del_arte docs/fase02_entorno_experimental/07_documentacion_subida_github.md docs/fase04_integracion_autopiloto src/control
git commit -m "Publish state of art and MAVLink control updates"
git push origin main
```

### Criterio de mantenimiento

Este archivo conserva el proceso historico de publicacion inicial y un resumen de hitos posteriores. Para cambios futuros, se recomienda actualizar esta seccion cuando exista un avance metodologico relevante, por ejemplo:

- cierre de una fase tecnica;
- incorporacion de un modulo nuevo;
- reorganizacion importante de documentacion;
- cambios de configuracion que afecten la reproducibilidad;
- validacion experimental relevante.
