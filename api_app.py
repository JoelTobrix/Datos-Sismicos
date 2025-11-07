# api_app.py
from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI(title="API Sísmica Ecuador", version="1.0")

# Cargar datos
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",")

# --- LIMPIAR NOMBRES DE COLUMNAS ---
df.columns = df.columns.str.strip()
df = df.rename(columns={
    'time_value': 'fecha',
    'latitude_value': 'lat',
    'longitude_value': 'lon',
    'depth_value': 'profundidad',
    'magnitude_value_M': 'magnitud'
})
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df["año"] = df["fecha"].dt.year

@app.get("/")
def raiz():
    return {"mensaje": "Bienvenido a la API de Sismos del Ecuador"}

@app.get("/sismos")
def obtener_sismos(
    mag_min: float = Query(4.0, description="Magnitud mínima"),
    mag_max: float = Query(7.0, description="Magnitud máxima"),
    año: int = Query(None, description="Año específico (opcional)")
):
    df_filtrado = df[df["magnitud"].between(mag_min, mag_max)]
    if año:
        df_filtrado = df_filtrado[df_filtrado["año"] == año]
    return df_filtrado.to_dict(orient="records")
