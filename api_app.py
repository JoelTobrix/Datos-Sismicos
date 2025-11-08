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

@app.get("/sismos/query")
def obtener_sismos(
    mag_min: float = Query(4.0, description="Magnitud mínima"),
    mag_max: float = Query(7.0, description="Magnitud máxima"),
    año: int = Query(None, description="Año específico (opcional)")
):
    df_filtrado = df[df["magnitud"].between(mag_min, mag_max)]
    if año:
        df_filtrado = df_filtrado[df_filtrado["año"] == año]
    return df_filtrado.to_dict(orient="records")

@app.get("/sismos/categories")
def obtener_categorias(
group_by: str = Query("magnitud", description="Agrupar por 'magnitud' o 'profundidad'")

):
     # --- Definir  categorías de magnitud ---
    bins_magnitud = [0, 2, 4, 5, 6, 7, 8, 10]
    labels_magnitud = ["Micro", "Menor", "Ligero", "Moderado", "Fuerte", "Mayor", "Gran"]
    df["categoria_magnitud"] = pd.cut(df["magnitud"], bins=bins_magnitud, labels=labels_magnitud, right=False)

    # --- Definir  categorías de profundidad ---
    bins_profundidad = [0, 30, 70, 300, 700]
    labels_profundidad = ["Superficial", "Intermedia", "Profunda", "Muy profunda"]
    df["categoria_profundidad"] = pd.cut(df["profundidad"], bins=bins_profundidad, labels=labels_profundidad, right=False)

    # --- Determinar  columna a agrupar ---
    group_col = None
    if group_by.lower() == "magnitud":
        group_col = 'categoria_magnitud'
    elif group_by.lower() == "profundidad":
        group_col = 'categoria_profundidad'
    else:
        return {"error": "Parámetro inválido. Usa 'magnitud' o 'profundidad'."}

    # --- Agrupar y contar ---
    resumen = df[group_col].value_counts().sort_index()

    return {
        "tipo_agrupacion": group_by,
        "resumen": resumen.to_dict()
    }

