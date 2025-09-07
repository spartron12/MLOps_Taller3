#!/bin/bash
# auto_start_dag.sh
# Script para activar y ejecutar automáticamente el DAG

echo "🚀 Iniciando configuración automática de Airflow..."

# Esperar a que Airflow esté completamente iniciado
echo "⏳ Esperando que Airflow esté disponible..."
sleep 90

# Activar el DAG (despausar)
echo "🔓 Activando DAG 'orquestador'..."
airflow dags unpause orquestador

# Verificar que el DAG esté activo
DAG_STATE=$(airflow dags state orquestador)
echo "📊 Estado del DAG: $DAG_STATE"

# Ejecutar el DAG una vez
echo "▶️ Disparando ejecución del DAG 'orquestador'..."
airflow dags trigger orquestador

# Confirmar que se disparó
echo "✅ DAG disparado exitosamente!"
echo "🔍 Puedes monitorear el progreso en: http://localhost:8080"

# Opcional: Mostrar el estado de las tareas
sleep 10
echo "📈 Estado de las tareas:"
airflow tasks list orquestador