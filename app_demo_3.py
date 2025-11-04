# app_demo_3.py
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor Sísmico Ecuador - Demo 3", layout="wide")

st.title(" Monitor Sísmico - Ecuador (Demo 3)")
st.markdown("Distribución de **magnitudes sísmicas** registradas en Ecuador (2012–2025)")

# --- CARGAR DATOS ---
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",", engine="python")

# --- LIMPIAR COLUMNAS ---
df.columns = df.columns.str.strip()

# --- RENOMBRAR COLUMNAS ---
df = df.rename(columns={
    'time_value': 'fecha',
    'latitude_value': 'lat',
    'longitude_value': 'lon',
    'depth_value': 'profundidad',
    'magnitude_value_M': 'magnitud'
})

# --- ELIMINAR REGISTROS SIN MAGNITUD ---
df = df.dropna(subset=['magnitud'])

# --- CONVERTIR FECHA ---
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['año'] = df['fecha'].dt.year

# --- FILTROS LATERALES ---
st.sidebar.header("🎚️ Filtros")

# Filtro por rango de años
año_min, año_max = int(df['año'].min()), int(df['año'].max())
rango_años = st.sidebar.slider(
    "Selecciona el rango de años",
    año_min, año_max,
    (año_min, año_max)
)

# Filtro de profundidad
prof_min, prof_max = float(df['profundidad'].min()), float(df['profundidad'].max())
rango_profundidad = st.sidebar.slider(
    "Selecciona el rango de profundidad (km)",
    prof_min, prof_max,
    (prof_min, prof_max)
)

# --- FILTRAR DATOS ---
df_filtrado = df[
    (df['año'].between(rango_años[0], rango_años[1])) &
    (df['profundidad'].between(rango_profundidad[0], rango_profundidad[1]))
]

# --- HISTOGRAMA DE MAGNITUDES ---
st.subheader("📈 Distribución de magnitudes")

fig = px.histogram(
    df_filtrado,
    x='magnitud',
    nbins=20,
    color_discrete_sequence=['royalblue'],
    title="Histograma de magnitudes sísmicas",
    labels={'magnitud': 'Magnitud', 'count': 'Frecuencia'}
)

fig.update_traces(marker_line_width=1, marker_line_color="white")
fig.update_layout(bargap=0.1)

st.plotly_chart(fig, use_container_width=True)

# --- INFORMACIÓN ---
st.markdown("---")
st.markdown("**Fuente de datos:** Instituto Geofísico EPN | Catálogo de sismos 2012–2025")