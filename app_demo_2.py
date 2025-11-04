## app_demo_2.py
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor Sísmico Ecuador - Demo 2", layout="wide")

st.title("🌋 Monitor Sísmico - Ecuador (Demo 2)")
st.markdown("Visualización del número de sismos por **año** en Ecuador")

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

# --- CONVERTIR FECHA ---
if 'fecha' not in df.columns:
    st.error(" No se encontró la columna 'fecha' en los datos.")
    st.stop()

df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['año'] = df['fecha'].dt.year

# --- ELIMINAR REGISTROS SIN FECHA ---
df = df.dropna(subset=['año'])

# --- FILTRO DE MAGNITUD ---
st.sidebar.header("🎚️ Filtros")
mag_min, mag_max = st.sidebar.slider(
    "Selecciona el rango de magnitud",
    float(df["magnitud"].min()),
    float(df["magnitud"].max()),
    (4.0, 7.0)
)

df_filtrado = df[df["magnitud"].between(mag_min, mag_max)]

# --- AGRUPAR POR AÑO ---
conteo_anual = df_filtrado.groupby('año').size().reset_index(name='cantidad')

# --- GRÁFICO DE BARRAS ---
st.subheader(" Número de sismos por año")

fig = px.bar(
    conteo_anual,
    x='año',
    y='cantidad',
    text='cantidad',
    color='cantidad',
    color_continuous_scale='plasma',
    labels={'cantidad': 'Número de sismos', 'año': 'Año'},
    title="Tendencia anual de la actividad sísmica"
)

fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# --- INFORMACIÓN ---
st.markdown("---")
st.markdown("**Fuente de datos:** Instituto Geofísico EPN | Catálogo de sismos 2012–2025")