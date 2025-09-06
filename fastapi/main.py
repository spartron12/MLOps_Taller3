#fastapi_app.py - Versión simplificada para tu modelo Random Forest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
import joblib
import pickle
import logging
import os

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instanciar FastAPI
app = FastAPI(
    title="Penguins Species Prediction API",
    description="API para predecir especies de pingüinos usando Regresion Logistica",
    version="1.0.0"
)

# Variables globales
model = None
species_mapping = {1: "Adelie", 2: "Chinstrap", 3: "Gentoo"}

# Esquema de entrada
class PenguinFeatures(BaseModel):
    bill_length_mm: float = Field(..., example=39.1, description="Longitud del pico en mm")
    bill_depth_mm: float = Field(..., example=18.7, description="Profundidad del pico en mm")
    flipper_length_mm: float = Field(..., example=181.0, description="Longitud de la aleta en mm")
    body_mass_g: float = Field(..., example=3750.0, description="Masa corporal en gramos")
    year: int = Field(..., example=2007, description="Año de observación")
    # Variables dummy para isla y sexo
    island_Biscoe: int = Field(0, example=0, description="1 si es isla Biscoe, 0 si no")
    island_Dream: int = Field(0, example=0, description="1 si es isla Dream, 0 si no")  
    island_Torgersen: int = Field(1, example=1, description="1 si es isla Torgersen, 0 si no")
    sex_female: int = Field(0, example=0, description="1 si es hembra, 0 si no")
    sex_male: int = Field(1, example=1, description="1 si es macho, 0 si no")

# Cargar modelo al iniciar
@app.on_event("startup")
async def load_model():
    global model
    try:
        model_path = "/opt/airflow/models/RegresionLogistica.pkl"
        
        # Cargar el modelo
        with open(model_path, 'rb') as f:
            model = joblib.load(f)
        
        logger.info("Modelo RegresionLogistica cargado exitosamente")
        logger.info(f"Tipo de modelo: {type(model)}")
        
        # Verificar que puede hacer predicciones
        test_data = np.array([[39.1, 18.7, 181.0, 3750.0, 2007, 0, 0, 1, 0, 1]])
        test_prediction = model.predict(test_data)
        logger.info(f"Predicción de prueba: {test_prediction}")
        
    except Exception as e:
        logger.error(f"Error cargando modelo: {str(e)}")
        raise e



# Endpoint de predicción
@app.post("/predict")
def predict(features: PenguinFeatures):
    """Predecir la especie de pingüino"""
    
    # Verificar que el modelo está cargado
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Construir array de características en el orden correcto
        # Basado en tu función clean(): bill_length_mm, bill_depth_mm, flipper_length_mm, 
        # body_mass_g, year, island_Biscoe, island_Dream, island_Torgersen, sex_female, sex_male
        X = np.array([[
            features.bill_length_mm,
            features.bill_depth_mm, 
            features.flipper_length_mm,
            features.body_mass_g,
            features.year,
            features.island_Biscoe,
            features.island_Dream,
            features.island_Torgersen,
            features.sex_female,
            features.sex_male
        ]])
        
        logger.info(f"Datos de entrada: {X}")
        
        # Hacer predicción
        prediction = model.predict(X)[0]
        
        # Obtener probabilidades si el modelo las soporta
        probabilities = None
        prob_dict = None
        if hasattr(model, 'predict_proba'):
            try:
                probabilities = model.predict_proba(X)[0]
                prob_dict = {
                    species_mapping[i+1]: float(prob) 
                    for i, prob in enumerate(probabilities)
                }
            except Exception as e:
                logger.warning(f"No se pudieron obtener probabilidades: {str(e)}")
        
        # Preparar respuesta
        response = {
            "species_id": int(prediction),
            "species_name": species_mapping.get(prediction, "Desconocido"),
            "model_used": "RegresionLogistica",
            "input_features": {
                "bill_length_mm": features.bill_length_mm,
                "bill_depth_mm": features.bill_depth_mm,
                "flipper_length_mm": features.flipper_length_mm,
                "body_mass_g": features.body_mass_g,
                "year": features.year,
                "island": "Biscoe" if features.island_Biscoe else ("Dream" if features.island_Dream else "Torgersen"),
                "sex": "female" if features.sex_female else "male"
            }
        }
        
        # Agregar probabilidades si están disponibles
        if prob_dict:
            response["probabilities"] = prob_dict
        
        logger.info(f"Predicción exitosa: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error en predicción: {str(e)}")

# Endpoint para información del modelo
@app.get("/model-info")
def model_info():
    """Obtener información sobre el modelo cargado"""
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    info = {
        "model_type": str(type(model).__name__),
        "model_loaded": True
    }
    
    return info

# Endpoint de ejemplo para documentación
@app.get("/predict/example")
def prediction_example():
    """Ejemplo de cómo usar el endpoint de predicción"""
    return {
        "url": "/predict",
        "method": "POST",
        "example_request": {
            "bill_length_mm": 39.1,
            "bill_depth_mm": 18.7,
            "flipper_length_mm": 181.0,
            "body_mass_g": 3750.0,
            "year": 2007,
            "island_Biscoe": 0,
            "island_Dream": 0,
            "island_Torgersen": 1,
            "sex_female": 0,
            "sex_male": 1
        },
        "expected_response": {
            "species_id": 1,
            "species_name": "Adelie",
            "model_used": "RandomForestClassifier"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


