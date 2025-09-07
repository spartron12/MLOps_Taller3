# MLOps Taller 3 - Pipeline Automatizado con Airflow

**Grupo compuesto por Sebastian Rodríguez y David Córdova**

Este proyecto implementa un pipeline completo de Machine Learning Operations (MLOps) que automatiza desde la limpieza de datos hasta el entrenamiento de modelos y despliegue de API, utilizando Apache Airflow como orquestador principal.

## Características Principales

- Pipeline completamente automatizado con ejecución sin intervención manual
- Orquestación inteligente del flujo de trabajo con Apache Airflow
- Contenerización completa mediante Docker Compose
- Base de datos MySQL para almacenamiento persistente
- API FastAPI para servicio de predicciones en tiempo real
- Auto-trigger del DAG con activación automática al iniciar
- Dashboard web de Airflow para monitoreo en tiempo real

## Estructura del Proyecto

```
MLOps_Taller3/
├── dags/
│   ├── scripts/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── funciones.py
│   │   └── queries.py
│   ├── fastapi_ready.txt
│   ├── fastapi.log
│   └── orquestador.py
├── fastapi/
│   ├── __pycache__/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── logs/
├── models/
├── plugins/
├── images/
├── .env
├── docker-compose.yaml
└── README.md
```

### Descripción de Componentes

- **dags/**:
  - **orquestador.py**: DAG principal de Airflow que automatiza todo el pipeline de Machine Learning
  - **scripts/funciones.py**: Funciones principales del pipeline (insert_data,clean, read_data, train_model)
  - **scripts/queries.py**: Consultas SQL para creación y manipulación de tablas en MySQL
  - **fastapi_ready.txt**: Archivo de señal para indicar que FastAPI está listo
  - **fastapi.log**: Logs del servicio FastAPI

- **fastapi/**:
  - **main.py**: Aplicación principal de FastAPI que consume los modelos entrenados
  - **Dockerfile**: Contenerización del servicio API
  - **requirements.txt**: Dependencias específicas para el servicio FastAPI

- **models/**:
  - Carpeta compartida que almacena los modelos entrenados en formato pickle (.pkl)
  - Es montada como volumen en todos los contenedores que necesitan acceso a los modelos
  - Contiene archivos como: `RegresionLogistica.pkl`

- **logs/**: Directorio donde Airflow almacena todos los logs de ejecución de tareas y DAGs
- **plugins/**: Directorio para plugins personalizados de Airflow (vacío por defecto)
- **images/**: Carpeta para almacenar capturas de pantalla y evidencias del funcionamiento

- **.env**: 
  - Archivo de variables de entorno que configura automáticamente las credenciales de Airflow
  - Elimina la necesidad de configuración manual con credenciales predeterminadas (admin/admin)

- **docker-compose.yaml**:
  - Archivo de orquestación que define y gestiona todos los contenedores del proyecto
  - Incluye servicios para: Airflow (webserver, scheduler, worker, triggerer), MySQL, Redis, PostgreSQL, FastAPI
  - Contiene el servicio `dag-auto-trigger` que ejecuta automáticamente el pipeline después del inicio



## Automatización Implementada

### Por qué se automatizó

**Problema original:**
- Requería login manual en Airflow (`admin`/`admin`)
- Necesitaba activar DAGs manualmente
- Requería trigger manual del pipeline
- Intervención humana en múltiples pasos

**Solución automatizada:**
- Zero-touch deployment - Una sola ejecución automatiza todo
- Auto-activación de DAGs - Se activan automáticamente al iniciar
- Auto-trigger del pipeline - Se ejecuta automáticamente una vez
- Credenciales simplificadas - Admin/admin predeterminado

### Componentes de Automatización

#### Archivo .env - Configuración Automática

```bash
# Variables de entorno para automatización
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
AIRFLOW_PROJ_DIR=.
```

**Función:** Elimina la necesidad de configuración manual de credenciales.

#### docker-compose.yaml - Orquestación Automática

**Características de automatización implementadas:**

```yaml
# DAGs activos por defecto (sin intervención manual)
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'false'

# Detección rápida de cambios en DAGs
AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL: 30
AIRFLOW__SCHEDULER__PARSING_PROCESSES: 2
```

**Servicio de Auto-Trigger integrado:**
```yaml
dag-auto-trigger:
  command: >
    bash -c "
      echo 'Iniciando auto-trigger del DAG...'
      sleep 120
      echo 'Activando DAG orquestador...'
      airflow dags unpause orquestador || echo 'DAG ya está activo'
      echo 'Disparando ejecución del DAG...'
      airflow dags trigger orquestador
      echo 'DAG disparado exitosamente!'
    "
```

**Función:** Ejecuta automáticamente el pipeline 2 minutos después del inicio completo.


## Conexiones Configuradas

###  MySQL
```yaml
AIRFLOW_CONN_MYSQL_CONN: 'mysql://my_app_user:my_app_pass@mysql:3306/my_app_db'
````

* Permite conexión directa de **MySqlHook** y **MySqlOperator**
* Evita hardcodear credenciales en el código

### FileSensor

```yaml
AIRFLOW_CONN_FS_DEFAULT: 'fs:///'
```

* Usada por **FileSensor** para monitorear archivos del sistema
* Útil para pipelines basados en llegada de archivos

``

#### DAG Modificado - orquestador.py

**Configuración para auto-activación:**
```python
with DAG(
    dag_id="orquestador",
    schedule_interval=None,          # Ejecución controlada automáticamente
    catchup=False,
    is_paused_upon_creation=False,   # CLAVE: DAG activo desde creación
    tags=['ml', 'penguins', 'auto-execution']
) as dag:
```

**Función:** Garantiza que el DAG esté listo para ejecución automática.


## Flujo del Pipeline Automatizado

### Secuencia de Ejecución Automática:

1. docker-compose up
2. Servicios iniciando (MySQL + Redis + PostgreSQL)
3. Airflow Webserver + Scheduler
4. DAG auto-activo
5. Auto-trigger después de 120 segundos
6. Pipeline ML ejecutándose automáticamente


## DAG Orquestador (`orquestador.py`)

Este DAG orquesta todo el flujo de **ETL + entrenamiento de modelo** de pingüinos:

1. **Preparación de la base de datos**
   - Elimina tablas previas (`penguins_raw` y `penguins_clean`) si existen.
   - Crea las tablas necesarias para datos crudos y limpios.

2. **Carga y limpieza de datos**
   - Inserta datos de pingüinos en la tabla `penguins_raw`.
   - Limpia y transforma los datos (One-Hot Encoding, manejo de NaN) y los inserta en `penguins_clean`.

3. **Entrenamiento del modelo**
   - Usa los datos limpios para entrenar un modelo de **Regresión Logística**.
   - Guarda el modelo entrenado en `/opt/airflow/models/RegresionLogistica.pkl`.

4. **Validación del modelo**
   - Un `FileSensor` verifica que el archivo del modelo exista antes de finalizar el pipeline.

---

### Resumen del flujo

```
delete_table + delete_table_clean
         ↓
  create_table_raw
         ↓
 create_table_clean
         ↓
   insert_data
         ↓
    read_data
         ↓
   train_model
         ↓
wait_for_model_file (FileSensor)
```





**Resultado final:**  
Se obtiene un modelo de clasificación entrenado y validado automáticamente, listo para ser consumido desde FastAPI.








## Instrucciones de Ejecución

### Preparación Inicial

```bash
# Clonar el repositorio
git clone https://github.com/DAVID316CORDOVA/MLOps_Taller3.git
cd MLOps_Taller3

# Limpiar entorno previo (si existe)
docker-compose down -v
docker system prune -f
```

### Ejecución Completamente Automática (Recomendado)

```bash
# Después de la preparación inicial, simplemente:
docker-compose up
```

**Qué sucede automáticamente:**
- Se crean todos los contenedores necesarios
- Airflow inicia con credenciales admin/admin
- DAG se activa automáticamente
- Pipeline se ejecuta una vez automáticamente después de 2 minutos
- FastAPI queda disponible con modelo entrenado

### Ejecución en Background

```bash
# Para ejecutar en segundo plano
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f dag-auto-trigger
```

### Verificación Manual del Estado

```bash
# Verificar que Airflow esté disponible
curl -f http://localhost:8080/health

# Verificar estado de contenedores
docker-compose ps

# Acceder a la interfaz web
# http://localhost:8080 (admin/admin)
```

## Acceso a Servicios

| Servicio | URL | Credenciales | Descripción |
|----------|-----|--------------|-------------|
| **Airflow Web** | http://localhost:8080 | admin/admin | Dashboard del pipeline |
| **FastAPI Docs** | http://localhost:8000/docs | - | API de predicciones |
| **MySQL** | localhost:3306 | my_app_user/my_app_pass | Base de datos |
| **Flower (opcional)** | http://localhost:5555 | - | Monitor de Celery |

## Ejecución del Proyecto

### 1. Levantamiento de la aplicación
![Inicio del sistema](./images/compose.jpg)

### 2. Login de Airflow
![Inicio del sistema](./images/login.jpg)

### 3. Ejecución Automática del Pipeline - DAG Auto-Activo
![Inicio del sistema](./images/dag.jpg)

## 4. Visualización todos los tasks de Airflow ejecutándose automaticamente
![Inicio del sistema](./images/orquesta.jpg)

## 5. Visualización del correcto funcionamiento de la interfaz gráfica de FASTAPI 
![Inicio del sistema](./images/fastapi.jpg)


## 6. Predicción usando el modelo generado automáticamente por AirFlow
![Inicio del sistema](./images/fastapi_prediction.jpg)


## Funciones Técnicas Implementadas

### funciones.py - Lógica del Pipeline

```python
def insert_data():
    """Inserta datos de Palmer Penguins en MySQL"""
    # Carga dataset Palmer Penguins
    # Limpia valores nulos y NaN
    # Inserta registros en tabla MySQL `penguins_raw`

def clean(df):
    """Limpia y transforma los datos"""
    # Elimina registros con valores nulos
    # Aplica One-Hot Encoding para variables categóricas (island, sex)
    # Convierte columnas booleanas a enteros
    # Transforma species a valores numéricos (1=Adelie, 2=Chinstrap, 3=Gentoo)
    # Retorna DataFrame listo para almacenar en `penguins_clean`

def read_data():
    """Lee y procesa datos desde MySQL"""
    # Extrae registros desde tabla `penguins_raw`
    # Aplica limpieza y codificación con `clean()`
    # Inserta datos transformados en tabla `penguins_clean`

def train_model():
    """Entrena y guarda un modelo de Regresión Logística"""
    # Carga datos desde tabla `penguins_clean`
    # Divide dataset en entrenamiento y prueba
    # Entrena modelo de clasificación
    # Evalúa desempeño con métricas (accuracy, confusion matrix, classification report)
    # Guarda modelo en `/opt/airflow/models/RegresionLogistica.pkl`

def start_fastapi_server():
    """Prepara entorno FastAPI para servir el modelo"""
    # Verifica existencia del modelo entrenado
    # Configura aplicación FastAPI ubicada en `/opt/airflow/dags/fastapi_app.py`
    # Genera archivo de estado `fastapi_ready.txt`
    # Sugiere comando de despliegue con uvicorn

```

### queries.py - Consultas SQL

```sql
DROP_PENGUINS_TABLE = """
DROP TABLE IF EXISTS penguins_raw;
"""

DROP_PENGUINS_CLEAN_TABLE = """
DROP TABLE IF EXISTS penguins_clean;            
 """


CREATE_PENGUINS_TABLE_RAW = """ CREATE TABLE penguins_raw (
            species VARCHAR(50) NULL,
            island VARCHAR(50) NULL,
            bill_length_mm DOUBLE NULL,
            bill_depth_mm DOUBLE NULL,
            flipper_length_mm DOUBLE NULL,
            body_mass_g DOUBLE NULL,
            sex VARCHAR(10) NULL,
            year INT NULL
        )
        """

CREATE_PENGUINS_TABLE_CLEAN = """ CREATE TABLE penguins_clean (
    species INT NULL,
    bill_length_mm DOUBLE NULL,
    bill_depth_mm DOUBLE NULL,
    flipper_length_mm DOUBLE NULL,
    body_mass_g DOUBLE NULL,
    year INT NULL,
    island_Biscoe INT NULL,
    island_Dream INT NULL,
    island_Torgersen INT NULL,
    sex_female INT NULL,
    sex_male INT NULL
        );      
        """
"""

```









## Conclusiones

Este proyecto implementa un pipeline MLOps completamente automatizado que:

- Elimina intervención manual en el proceso de entrenamiento
- Proporciona un sistema reproducible y confiable
- Integra todas las fases del ciclo de vida del modelo
- Ofrece monitoreo y trazabilidad completa
- Reduce significativamente el tiempo de despliegue

La automatización establecida proporciona una base sólida para operaciones de Machine Learning en producción, minimizando errores humanos y maximizando la eficiencia operacional.

---

**Desarrollado por:**
- Sebastian Rodríguez  
- David Córdova

**Proyecto:** MLOps Taller 3 - Pipeline Automatizado  
**Fecha:** Septiembre 2025
