# Dashboard_app.py
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor Sísmico Ecuador - Dashboard", layout="wide")

st.title(" Monitor Sísmico - Ecuador")
st.markdown("Dashboard interactivo con mapa, gráficos y análisis básico de sismos 2012–2025")

# --- CARGAR DATOS ---
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",")

# --- LIMPIAR NOMBRES DE COLUMNAS ---
df.columns = df.columns.str.strip()

# --- RENOMBRAR COLUMNAS ---
df = df.rename(columns={
    'time_value': 'fecha',
    'latitude_value': 'lat',
    'longitude_value': 'lon',
    'depth_value': 'profundidad',
    'magnitude_value_M': 'magnitud'
})

# --- CONVERSIÓN DE FECHA ---
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df["año"] = df["fecha"].dt.year


# --- MENÚ DE NAVEGACIÓN ---
menu = st.sidebar.radio("Selecciona vista:", ["Mapa de Sismos", "Gráfico por Año", "Distribución de Magnitudes"])

# --- MAPA ---
if menu == "Mapa de Sismos":
    st.subheader("🗺️ Mapa interactivo de sismos")
    mag_min, mag_max = st.slider(
        "Rango de magnitud:",
        float(df["magnitud"].min()),
        float(df["magnitud"].max()),
        (4.0, 7.0)
    )
    df_filtrado = df[df["magnitud"].between(mag_min, mag_max)]

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

# --- GRÁFICO DE BARRAS ---
elif menu == "Gráfico por Año":
    st.subheader("📊 Número de sismos por año")
    conteo = df["año"].value_counts().sort_index()
    fig = px.bar(
        x=conteo.index,
        y=conteo.values,
        labels={"x": "Año", "y": "Número de sismos"},
        color=conteo.values,
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- HISTOGRAMA ---
elif menu == "Distribución de Magnitudes":
    st.subheader("📈 Distribución de magnitudes sísmicas")
    fig_hist = px.histogram(
        df,
        x="magnitud",
        nbins=30,
        title="Distribución de magnitudes",
        color_discrete_sequence=["#FF4B4B"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")
st.caption("Datos: Instituto Geofísico EPN | Catálogo de Sismos 2012–2025")
