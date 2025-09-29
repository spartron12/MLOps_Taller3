import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import OneHotEncoder
from airflow.providers.mysql.hooks.mysql import MySqlHook
import os 
from sklearn.linear_model import DecisionTree
from datetime import datetime

df = pd.read_csv('/home/estudiante/talleres/Proyecto2/covertype_small.csv')
print(df.head())

MODEL_PATH = "/opt/airflow/models/DecisionTree.pkl"
FASTAPI_APP_PATH = "/opt/airflow/dags/fastapi_app.py"
TABLE_NAME = "forest_raw"
CONN_ID = "mysql_conn"


def insert_data():
    """
    Función para insertar datos en la tabla MySQL
    """
    df = pd.read_csv('/home/estudiante/talleres/Proyecto2/covertype_small.csv')
    hook = MySqlHook(mysql_conn_id=CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        sql = f"""
        INSERT INTO {TABLE_NAME} 
        (Elevation, Aspect, Slope,
         Horizontal_Distance_To_Hydrology, Vertical_Distance_To_Hydrology, Horizontal_Distance_To_Roadways,
         Hillshade_9am, Hillshade_Noon, Hillshade_3pm,
         Horizontal_Distance_To_Fire_Points, Wilderness_Area, Soil_Type, Cover_Type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            int(row["Elevation"]),
            int(row["Aspect"]),
            int(row["Slope"]),
            int(row["Horizontal_Distance_To_Hydrology"]),
            int(row["Vertical_Distance_To_Hydrology"]),
            int(row["Horizontal_Distance_To_Roadways"]),
            int(row["Hillshade_9am"]),
            int(row["Hillshade_Noon"]),
            int(row["Hillshade_3pm"]),
            int(row["Horizontal_Distance_To_Fire_Points"]),
            row["Wilderness_Area"] if pd.notna(row["Wilderness_Area"]) else None,
            row["Soil_Type"] if pd.notna(row["Soil_Type"]) else None,
            int(row["Cover_Type"])
        )
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()


def clean(df):
    df[df.isna().any(axis=1)]
    df.dropna(inplace=True)
    categorical_columns = ['Wilderness_Area', 'Soil_Type']
    df_encoded = pd.get_dummies(df, columns=categorical_columns).astype(int)
    return df_encoded


def read_data():
    hook = MySqlHook(mysql_conn_id=CONN_ID)

    # 1. Leer datos desde la tabla raw
    query = "SELECT * FROM forest_raw"
    df = hook.get_pandas_df(sql=query)

    # 2. Limpiar datos
    cleaned_df = clean(df)

    print(cleaned_df.head())
    print("Datos limpios listos para insertar en forest_onehot")
    print(cleaned_df.columns)

    # 3. Insertar en forest_onehot
    insert_sql = """
    INSERT INTO forest_clean (
        Elevation, Aspect, Slope,
        Horizontal_Distance_To_Hydrology, Vertical_Distance_To_Hydrology, Horizontal_Distance_To_Roadways,
        Hillshade_9am, Hillshade_Noon, Hillshade_3pm,
        Horizontal_Distance_To_Fire_Points, Cover_Type,
        Wilderness_Area_Cache, Wilderness_Area_Commanche, Wilderness_Area_Neota, Wilderness_Area_Rawah,
        Soil_Type_C2702, Soil_Type_C2703, Soil_Type_C2704, Soil_Type_C2705, Soil_Type_C2706, Soil_Type_C2717,
        Soil_Type_C3502, Soil_Type_C4201, Soil_Type_C4703, Soil_Type_C4704, Soil_Type_C4744, Soil_Type_C4758,
        Soil_Type_C5101, Soil_Type_C6101, Soil_Type_C6102, Soil_Type_C6731, Soil_Type_C7101, Soil_Type_C7102,
        Soil_Type_C7103, Soil_Type_C7201, Soil_Type_C7202, Soil_Type_C7700, Soil_Type_C7701, Soil_Type_C7702,
        Soil_Type_C7709, Soil_Type_C7710, Soil_Type_C7745, Soil_Type_C7746, Soil_Type_C7755, Soil_Type_C7756,
        Soil_Type_C7757, Soil_Type_C7790, Soil_Type_C8703, Soil_Type_C8707, Soil_Type_C8708,
        Soil_Type_C8771, Soil_Type_C8772, Soil_Type_C8776
    )
    VALUES (
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s
    )
    """

    values = [
        (
            int(row["Elevation"]),
            int(row["Aspect"]),
            int(row["Slope"]),
            int(row["Horizontal_Distance_To_Hydrology"]),
            int(row["Vertical_Distance_To_Hydrology"]),
            int(row["Horizontal_Distance_To_Roadways"]),
            int(row["Hillshade_9am"]),
            int(row["Hillshade_Noon"]),
            int(row["Hillshade_3pm"]),
            int(row["Horizontal_Distance_To_Fire_Points"]),
            int(row["Cover_Type"]),
            int(row["Wilderness_Area_Cache"]),
            int(row["Wilderness_Area_Commanche"]),
            int(row["Wilderness_Area_Neota"]),
            int(row["Wilderness_Area_Rawah"]),
            int(row["Soil_Type_C2702"]),
            int(row["Soil_Type_C2703"]),
            int(row["Soil_Type_C2704"]),
            int(row["Soil_Type_C2705"]),
            int(row["Soil_Type_C2706"]),
            int(row["Soil_Type_C2717"]),
            int(row["Soil_Type_C3502"]),
            int(row["Soil_Type_C4201"]),
            int(row["Soil_Type_C4703"]),
            int(row["Soil_Type_C4704"]),
            int(row["Soil_Type_C4744"]),
            int(row["Soil_Type_C4758"]),
            int(row["Soil_Type_C5101"]),
            int(row["Soil_Type_C6101"]),
            int(row["Soil_Type_C6102"]),
            int(row["Soil_Type_C6731"]),
            int(row["Soil_Type_C7101"]),
            int(row["Soil_Type_C7102"]),
            int(row["Soil_Type_C7103"]),
            int(row["Soil_Type_C7201"]),
            int(row["Soil_Type_C7202"]),
            int(row["Soil_Type_C7700"]),
            int(row["Soil_Type_C7701"]),
            int(row["Soil_Type_C7702"]),
            int(row["Soil_Type_C7709"]),
            int(row["Soil_Type_C7710"]),
            int(row["Soil_Type_C7745"]),
            int(row["Soil_Type_C7746"]),
            int(row["Soil_Type_C7755"]),
            int(row["Soil_Type_C7756"]),
            int(row["Soil_Type_C7757"]),
            int(row["Soil_Type_C7790"]),
            int(row["Soil_Type_C8703"]),
            int(row["Soil_Type_C8707"]),
            int(row["Soil_Type_C8708"]),
            int(row["Soil_Type_C8771"]),
            int(row["Soil_Type_C8772"]),
            int(row["Soil_Type_C8776"]),
        )
        for _, row in cleaned_df.iterrows()
    ]

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.executemany(insert_sql, values)
    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Limpieza e inserción terminada en forest_clean")



def train_model():
    # Conexión a la base de datos para obtener los datos
    hook = MySqlHook(mysql_conn_id=CONN_ID)
    query = "SELECT * FROM forest_clean"
    df = hook.get_pandas_df(sql=query)

    # Definir las características y la variable objetivo
    X = df.drop('Cover_Type', axis=1)
    y = df['Cover_Type']
    
    from imblearn.combine import SMOTEENN

    imp=SMOTEENN(sampling_strategy="all")

    X_bal,y_bal=imp.fit_resample(X,y)

    #Finding out if the imbalaced data continues

    y_bal.value_counts(normalize=True)*100

    X_train, X_test, Y_train, Y_test = train_test_split(
    X_bal, y_bal, test_size=0.2, random_state=42, stratify= y_bal)
    
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(Y_test, y_pred))


    # Guardar el modelo entrenado en el directorio especificado
    os.makedirs('/opt/airflow/models', exist_ok=True)
    joblib.dump(model, '/opt/airflow/models/DecisionTree.pkl')


def start_fastapi_server():
    """
    Función para verificar que el modelo existe y preparar FastAPI
    """
    import subprocess
    import time
    
    # Verificar que el modelo existe
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}")
    

    # Comando para iniciar FastAPI (en background)

    try:
        
        print(" Configuración de FastAPI lista:")
        print(f"   - Modelo: {MODEL_PATH}")
        print(f"   - App: {FASTAPI_APP_PATH}")
        print("   - Puerto sugerido: 8000")
        print("   - Comando sugerido: uvicorn fastapi_app:app --host 0.0.0.0 --port 8000")
        
       
        with open("/opt/airflow/dags/fastapi_ready.txt", "w") as f:
            f.write(f"FastAPI ready at {datetime.now()}\n")
            f.write(f"Model path: {MODEL_PATH}\n")
        
        print(" FastAPI configurado y listo para usar")
        
    except Exception as e:
        print(f"Error configurando FastAPI: {str(e)}")
        raise    