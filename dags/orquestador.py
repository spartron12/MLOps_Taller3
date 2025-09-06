import sys
import os
from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from airflow.operators.bash import BashOperator
from funciones import  insert_data, read_data, train_model, start_fastapi_server
from scripts.queries import DROP_PENGUINS_TABLE, CREATE_PENGUINS_TABLE_RAW, CREATE_PENGUINS_TABLE_CLEAN, DROP_PENGUINS_CLEAN_TABLE


MODEL_PATH = "/opt/airflow/models/RegresionLogistica.pkl"

with DAG(
    dag_id="orquestador",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@once",
    catchup=False,
) as dag:
#Borrado de tablas si existen
    # ========== PREPARACIÓN DE LA BASE DE DATOS =========
    delete_table = MySqlOperator(
        task_id="delete_table",
        mysql_conn_id="mysql_conn",
        sql=DROP_PENGUINS_TABLE,
    )

    delete_table_clean = MySqlOperator(
        task_id="delete_table-clean",
        mysql_conn_id="mysql_conn",
        sql=DROP_PENGUINS_CLEAN_TABLE,
    )
#Creación de tablas raw y clean 
    create_table_raw = MySqlOperator(
        task_id="create_table_raw",
        mysql_conn_id="mysql_conn",
        sql=CREATE_PENGUINS_TABLE_RAW,
    )

    create_table_clean = MySqlOperator(
        task_id="create_table_clean",
        mysql_conn_id="mysql_conn",
        sql= CREATE_PENGUINS_TABLE_CLEAN,
    )

#inserción de datos en tabla raw    
    insert_task = PythonOperator(
        task_id="insert_penguins",
        python_callable=insert_data,
    )
# ========== LIMPIEZA DE DATOS Y ENTRENAMIENTO DEL MODELO ==========
    read_task = PythonOperator(
        task_id="read_data",
        python_callable=read_data,
    )

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

# ========== SENSOR DE CARGA DEL MODELO ==========
    
    # Sensor que espera a que el archivo del modelo exista
    model_file_sensor = FileSensor(
        task_id="wait_for_model_file",
        filepath=MODEL_PATH,
        fs_conn_id="fs_default",  # Conexión por defecto del sistema de archivos
        poke_interval=30,  # Revisar cada 30 segundos
        timeout=60 * 10,   # Timeout de 10 minutos
        mode="poke"        # Modo poke (revisar periódicamente)
    )



    # ========== DESPLIEGUE API ==========
    
    # Preparar y configurar FastAPI
    # setup_fastapi = PythonOperator(
    #     task_id="setup_fastapi",
    #     python_callable=start_fastapi_server,
    # )
    


    # start_fastapi_server_bash = BashOperator(
    #     task_id="start_fastapi_server",
    #     bash_command=f"""
    #     cd /opt/airflow/dags && 
    #     nohup uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
    #     echo $! > fastapi.pid
    #     sleep 5
    #     echo "FastAPI server started with PID: $(cat fastapi.pid)"
    #     """,
    

    # )
    

# Flujo de proceso
[delete_table,  delete_table_clean] >> create_table_raw >> create_table_clean >> insert_task  >> read_task >> train_task >>  model_file_sensor 


