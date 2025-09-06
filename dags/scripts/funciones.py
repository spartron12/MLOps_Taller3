import palmerpenguins as pp
from palmerpenguins import load_penguins
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
from sklearn.linear_model import LogisticRegression
from datetime import datetime

df = pp.load_penguins()

MODEL_PATH = "/opt/airflow/models/RegresionLogistica.pkl"
FASTAPI_APP_PATH = "/opt/airflow/dags/fastapi_app.py"
TABLE_NAME = "penguins_raw"
CONN_ID = "mysql_conn"

def insert_data():
    import palmerpenguins as pp
    from palmerpenguins import load_penguins
    """
    Función para insertar datos en la tabla MySQL
    """

    df = pp.load_penguins()
    hook = MySqlHook(mysql_conn_id=CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        sql = f"""
        INSERT INTO {TABLE_NAME} 
        (species, island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex, year)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            row["species"],
            row["island"],
            None if pd.isna(row["bill_length_mm"]) else float(row["bill_length_mm"]),
            None if pd.isna(row["bill_depth_mm"]) else float(row["bill_depth_mm"]),
            None if pd.isna(row["flipper_length_mm"]) else float(row["flipper_length_mm"]),
            None if pd.isna(row["body_mass_g"]) else float(row["body_mass_g"]),
            row["sex"] if pd.notna(row["sex"]) else None,
            int(row["year"]),
        )
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()


def clean(df):
    df[df.isna().any(axis=1)]
    df.dropna(inplace=True)
    categorical_cols = ['sex','island']
    encoder = OneHotEncoder(handle_unknown='ignore')
    x = df.drop(columns=['species'])
    y = df['species']
    x_encoded = encoder.fit_transform(x[categorical_cols])
    X_numeric = x.drop(columns=categorical_cols)
    X_final = np.hstack((X_numeric.values, x_encoded.toarray()))

    df_encoded = pd.get_dummies(df, columns=['island','sex'])
    bool_cols = df_encoded.select_dtypes(include='bool').columns
    df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)
    df_encoded.head()
    df_encoded['species'] = df_encoded['species'].apply(lambda x: 
        1 if x == 'Adelie' else 
        2 if x == 'Chinstrap' else 
        3 if x == 'Gentoo' else 
        None)
    return df_encoded

def read_data():
    hook = MySqlHook(mysql_conn_id=CONN_ID)
    
    # 1. Leer datos desde la tabla raw
    query = "SELECT * FROM penguins_raw"
    df = hook.get_pandas_df(sql=query)

    # 2. Limpiar datos (tu función clean debe hacer get_dummies y NaN handling)
    cleaned_df = clean(df)

    print(cleaned_df.head())
    print(" Datos limpios listos para insertar en penguins_clean")
    print(cleaned_df.columns)
    # 3. Insertar en penguins_clean
    insert_sql = """
        INSERT INTO penguins_clean (
            species, bill_length_mm, bill_depth_mm, flipper_length_mm, 
            body_mass_g, year, island_Biscoe, island_Dream, island_Torgersen, 
            sex_female, sex_male
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            int(row["species"]),
            None if pd.isna(row["bill_length_mm"]) else float(row["bill_length_mm"]),
            None if pd.isna(row["bill_depth_mm"]) else float(row["bill_depth_mm"]),
            None if pd.isna(row["flipper_length_mm"]) else float(row["flipper_length_mm"]),
            None if pd.isna(row["body_mass_g"]) else float(row["body_mass_g"]),
            int(row["year"]),
            int(row["island_Biscoe"]),
            int(row["island_Dream"]),
            int(row["island_Torgersen"]),
            int(row["sex_female"]),
            int(row["sex_male"]),
        )
        for _, row in cleaned_df.iterrows()
    ]

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.executemany(insert_sql, values)
    conn.commit()
    cursor.close()
    conn.close()

    print(" Limpieza e inserción terminada en penguins_clean")


def train_model():
    # Conexión a la base de datos para obtener los datos
    hook = MySqlHook(mysql_conn_id=CONN_ID)
    query = "SELECT * FROM penguins_clean"
    df = hook.get_pandas_df(sql=query)

    # Definir las características y la variable objetivo
    X = df.drop('species', axis=1)
    Y = df['species']
    X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)

    # Guardar el modelo entrenado en el directorio especificado
    os.makedirs('/opt/airflow/models', exist_ok=True)
    joblib.dump(model, '/opt/airflow/models/RegresionLogistica.pkl')


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