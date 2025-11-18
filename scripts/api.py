import pandas as pd
from fastapi import FastAPI, Query
import pandas as pd

app = FastAPI(title="API Sísmica Ecuador", version="1.0")

# Cargar datos
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",")

# --- LIMPIEZA ---
df.columns = df.columns.str.strip()
df = df.rename(columns={
    'time_value': 'fecha',
    'latitude_value': 'lat',
    'longitude_value': 'lon',
    'depth_value': 'profundidad',
    'magnitude_value_M': 'magnitud'   # ESTA ES LA CORRECTA
})

df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df["año"] = df["fecha"].dt.year
df["magnitud"] = pd.to_numeric(df["magnitud"], errors="coerce")
df["profundidad"] = pd.to_numeric(df["profundidad"], errors="coerce")

@app.get("/")
def raiz():
    return {"mensaje": "Bienvenido a la API de Sismos del Ecuador"}

@app.get("/sismos/query")
def obtener_sismos(
    mag_min: float = Query(3.5, description="Magnitud mínima"),
    mag_max: float = Query(8.0, description="Magnitud máxima"),
    año: int = Query(None, description="Año específico (opcional)")
):
    dff = df[df["magnitud"].between(mag_min, mag_max)]
    if año:
        dff = dff[dff["año"] == año]
    return dff.to_dict(orient="records")

@app.get("/sismos/categories")
def obtener_categorias(
    group_by: str = Query("magnitud", description="Agrupar por 'magnitud' o 'profundidad'")
):
    # Categorías de magnitud
    bins_magnitud = [0, 2, 4, 5, 6, 7, 8, 10]
    labels_magnitud = ["Micro", "Menor", "Ligero", "Moderado", "Fuerte", "Mayor", "Gran"]
    df["cat_mag"] = pd.cut(df["magnitud"], bins=bins_magnitud, labels=labels_magnitud, right=False)

    # Categorías de profundidad
    bins_profundidad = [0, 30, 70, 300, 700]
    labels_profundidad = ["Superficial", "Intermedia", "Profunda", "Muy profunda"]
    df["cat_prof"] = pd.cut(df["profundidad"], bins=bins_profundidad, labels=labels_profundidad, right=False)

    if group_by == "magnitud":
        resumen = df["cat_mag"].value_counts().sort_index()
    else:
        resumen = df["cat_prof"].value_counts().sort_index()

    return {"grupo": group_by, "resumen": resumen.to_dict()}