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
  - **scripts/funciones.py**: Funciones principales del pipeline (insert_data, read_data, train_model)
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

### Problema Original vs Solución

| **Antes (Manual)** | **Después (Automatizado)** |
|--------------------|-----------------------------|
| Login manual requerido | Credenciales admin/admin predeterminadas |
| Activar DAGs manualmente | DAG activo automáticamente al iniciar |
| Trigger manual del pipeline | Auto-trigger programado después de 120s |
| 5-7 pasos manuales | 1 comando: `docker-compose up` |
| Riesgo de errores humanos | Proceso 100% confiable |

### Componentes Clave de Automatización

#### Archivo .env - Configuración Automática
```bash
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
AIRFLOW_PROJ_DIR=.
```

#### docker-compose.yaml - Configuración Automática
```yaml
# DAGs activos por defecto
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'false'

# Servicio que ejecuta automáticamente el DAG
dag-auto-trigger:
  command: >
    bash -c "
      sleep 120
      airflow dags unpause orquestador
      airflow dags trigger orquestador
    "
```

#### DAG orquestador.py - Auto-activación
```python
with DAG(
    dag_id="orquestador",
    schedule_interval=None,
    is_paused_upon_creation=False,  # DAG activo desde creación
    catchup=False
) as dag:
```

### Conexiones Configuradas

#### MySQL
```yaml
AIRFLOW_CONN_MYSQL_CONN: 'mysql://my_app_user:my_app_pass@mysql:3306/my_app_db'
```
- Permite conexión directa de `MySqlHook` y `MySqlOperator`
- Evita hardcodear credenciales en el código

#### FileSensor
```yaml
AIRFLOW_CONN_FS_DEFAULT: 'fs:///'
```
- Usada por `FileSensor` para monitorear archivos del sistema
- Útil para pipelines basados en llegada de archivos

## Flujo del Pipeline

### Secuencia de Ejecución:
1. **docker-compose up** inicia todos los servicios
2. Servicios base: MySQL, Redis, PostgreSQL
3. Airflow: Webserver, Scheduler, Worker
4. DAG se activa automáticamente
5. Auto-trigger ejecuta pipeline después de 120 segundos

### Tareas del DAG:
1. **delete_table** / **delete_table_clean** - Limpia tablas existentes
2. **create_table_raw** / **create_table_clean** - Crea estructura de tablas
3. **insert_penguins** - Carga dataset Palmer Penguins a MySQL
4. **read_data** - Procesa y limpia datos desde MySQL
5. **train_model** - Entrena modelo de Regresión Logística
6. **wait_for_model_file** - Verifica que modelo esté guardado
7. **pipeline_completion** - Confirma finalización exitosa

## Instrucciones de Ejecución

### Ejecución Automática

```bash
# Clonar repositorio
git clone https://github.com/DAVID316CORDOVA/MLOps_Taller3.git
cd MLOps_Taller3

# Limpiar entorno previo
docker compose down -v
docker system prune -f

# Ejecutar pipeline completo
docker compose up
```

### Monitoreo Opcional

```bash
# Ejecución en background
docker compose up -d

# Ver logs del auto-trigger
docker compose logs -f dag-auto-trigger

# Verificar estado
docker compose ps
```

## Acceso a Servicios

| Servicio | URL | Credenciales | Descripción |
|----------|-----|--------------|-------------|
| **Airflow Web** | http://localhost:8080 | admin/admin | Dashboard del pipeline |
| **FastAPI Docs** | http://localhost:8000/docs | - | API de predicciones |
| **MySQL** | localhost:3306 | my_app_user/my_app_pass | Base de datos |

## Evidencia Visual

### 1. Levantamiento de la aplicación
![Inicio del sistema](./images/compose.jpg)

### 2. Login de Airflow
![Login Airflow](./images/login.jpg)

### 3. DAG Auto-Activo
![DAG Activo](./images/dag.jpg)

### 4. Ejecución de Tasks Automática
![Orquestación](./images/orquesta.jpg)

### 5. Interfaz FastAPI Funcionando
![FastAPI Interface](./images/fastapi.jpg)

### 6. Predicción con Modelo Entrenado
![Predicción](./images/fastapi_prediction.jpg)

## Implementación Técnica

### funciones.py - Lógica del Pipeline

```python
def insert_data():
    """Inserta datos de Palmer Penguins en MySQL"""
    # Carga dataset, limpia NaN, inserta en tabla raw

def clean(df):
    """Limpia y transforma datos"""
    # One-Hot Encoding, conversión de species a numérico
    # Retorna DataFrame procesado

def read_data():
    """Procesa datos desde MySQL"""
    # Extrae desde raw, aplica limpieza, guarda en clean

def train_model():
    """Entrena modelo de clasificación"""
    # Carga datos clean, entrena Regresión Logística
    # Guarda en /opt/airflow/models/RegresionLogistica.pkl
```

### queries.py - Consultas SQL

```sql
CREATE_PENGUINS_TABLE_RAW = """
CREATE TABLE penguins_raw (
    species VARCHAR(50), island VARCHAR(50),
    bill_length_mm DOUBLE, bill_depth_mm DOUBLE,
    flipper_length_mm DOUBLE, body_mass_g DOUBLE,
    sex VARCHAR(10), year INT
)"""

CREATE_PENGUINS_TABLE_CLEAN = """
CREATE TABLE penguins_clean (
    species INT, bill_length_mm DOUBLE, bill_depth_mm DOUBLE,
    flipper_length_mm DOUBLE, body_mass_g DOUBLE, year INT,
    island_Biscoe INT, island_Dream INT, island_Torgersen INT,
    sex_female INT, sex_male INT
)"""
```

## Tecnologías Utilizadas

| Categoría | Tecnología | Propósito |
|-----------|------------|-----------|
| **Orquestación** | Apache Airflow 2.6.0 | Automatización de pipeline |
| **Contenerización** | Docker + Docker Compose | Orquestación de servicios |
| **Base de Datos** | MySQL 8.0 | Persistencia de datos |
| **Cache/Queue** | Redis + PostgreSQL | Backend de Airflow |
| **API Framework** | FastAPI + Uvicorn | Servicio de modelos |
| **ML Libraries** | scikit-learn, pandas | Entrenamiento de modelos |

## Monitoreo y Logs

### Ubicación de Logs
- **Airflow**: `./logs/`
- **FastAPI**: `./dags/fastapi.log`
- **Contenedores**: `docker compose logs [service-name]`

### Comandos de Monitoreo
```bash
# Logs en tiempo real
docker compose logs -f

# Estado de contenedores
docker compose ps

# Uso de recursos
docker stats
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
