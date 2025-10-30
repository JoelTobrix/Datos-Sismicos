import pandas as pd
from fastapi import FastAPI, Query
from datetime import date
import os

app = FastAPI()

# Cargar los datos al iniciar la API
RUTA_PROCESADA = os.path.join(os.path.dirname(__file__), "..", "data", "processed_catalogo.csv")

try:
    df_sismos = pd.read_csv(RUTA_PROCESADA)
    df_sismos['time_value'] = pd.to_datetime(df_sismos['time_value'])
except FileNotFoundError:
    print(f"Error: No se encontró el archivo procesado en {RUTA_PROCESADA}. Ejecuta main.py primero.")
    df_sismos = pd.DataFrame()  # Crear un DataFrame vacío para evitar errores

# --- Endpoint para consultar sismos ---
@app.get("/sismos/query")
def query_sismos(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    min_magnitude: float = Query(3.5, description="Magnitud mínima")
):
    """
    Filtra los sismos por rango de fechas y magnitud mínima.
    """
    if df_sismos.empty:
        return {"error": "Datos no cargados. Verifique el log de la API."}

    # Convertir los parámetros a datetime
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # Filtrar por fechas y magnitud
    filtro_fecha = (df_sismos['time_value'] >= start_dt) & (df_sismos['time_value'] <= end_dt)
    filtro_magnitud = df_sismos['magnitude_value_P'] >= min_magnitude

    # Aplicar filtros
    df_filtrado = df_sismos[filtro_fecha & filtro_magnitud]

    # Devolver resultados como JSON
    return df_filtrado.to_dict(orient='records')
