# app_demo_1.py
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Monitor Sísmico Ecuador - Demo 1", layout="wide")

st.title("Monitor Sísmico - Ecuador (Demo 1)")
st.markdown("Primer prototipo del mapa interactivo de sismos en Ecuador")

# --- CARGAR DATOS ---
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",", engine="python")

# --- LIMPIAR NOMBRES DE COLUMNAS ---
df.columns = df.columns.str.strip()

# Mostrar columnas detectadas
st.write("Columnas detectadas:", list(df.columns))
st.dataframe(df.head())

# --- RENOMBRAR COLUMNAS ---
df = df.rename(columns={
    'time_value': 'fecha',
    'latitude_value': 'lat',
    'longitude_value': 'lon',
    'depth_value': 'profundidad',
    'magnitude_value_M': 'magnitud'
})

# --- CONVERSIÓN DE FECHA ---
if 'fecha' in df.columns:
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
else:
    st.error(" No se encontró la columna 'fecha' en los datos. Verifica los nombres de columnas.")
    st.stop()

# --- FILTRO SIMPLE ---
mag_min, mag_max = st.slider(
    "Selecciona el rango de magnitud",
    float(df["magnitud"].min()),
    float(df["magnitud"].max()),
    (4.0, 7.0)
)

df_filtrado = df[df["magnitud"].between(mag_min, mag_max)]

# --- MAPA INTERACTIVO ---
st.subheader("🗺️ Mapa de sismos")
mapa = px.scatter_mapbox(
    df_filtrado,
    lat="lat",
    lon="lon",
    color="magnitud",
    size="magnitud",
    color_continuous_scale="hot",
    zoom=5,
    mapbox_style="open-street-map",
    hover_data=["fecha", "magnitud", "profundidad"]
)
st.plotly_chart(mapa, use_container_width=True)

st.markdown("---")
st.markdown("**Fuente de datos:** Instituto Geofísico EPN | Catálogo de sismos 2012–2025")
