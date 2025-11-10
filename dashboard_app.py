# dashboard_app.py
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor Sísmico Ecuador - Dashboard", layout="wide")

st.title("🌋 Monitor Sísmico del Ecuador")
st.markdown("Visualización interactiva de los sismos registrados entre 2012 y 2025")

# --- CARGAR DATOS ---
ruta_datos = "data/cat_origen_2012-jul2025.txt"
df = pd.read_csv(ruta_datos, comment="#", sep=",")
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

# --- FILTROS LATERALES ---
st.sidebar.header("Filtros de visualización")

años_disponibles = sorted(df["año"].dropna().unique().tolist())
año_sel = st.sidebar.multiselect("Seleccionar año(s):", años_disponibles, default=años_disponibles[-3:])

mag_min, mag_max = st.sidebar.slider(
    "Rango de magnitud:",
    float(df["magnitud"].min()),
    float(df["magnitud"].max()),
    (4.0, 7.0)
)

prof_max = st.sidebar.slider(
    "Profundidad máxima (km):",
    float(df["profundidad"].min()),
    float(df["profundidad"].max()),
    float(df["profundidad"].max())
)

# --- FILTRO DE DATOS ---
df_filtrado = df[
    (df["año"].isin(año_sel)) &
    (df["magnitud"].between(mag_min, mag_max)) &
    (df["profundidad"] <= prof_max)
]

# --- MENÚ DE NAVEGACIÓN ---
menu = st.sidebar.radio(
    "Selecciona vista:",
    [
        "🗺️ Mapa de Sismos",
        "📊 Sismos por Año",
        "📈 Distribución de Magnitudes",
        "📉 Relación Magnitud–Profundidad"
    ]
)

# --- MAPA INTERACTIVO ---
if menu == "🗺️ Mapa de Sismos":
    st.subheader("🗺️ Mapa interactivo de sismos")
    st.write(f"Mostrando **{len(df_filtrado)} sismos** en el rango seleccionado.")
    
    fig_map = px.scatter_mapbox(
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
    st.plotly_chart(fig_map, use_container_width=True)

# --- GRÁFICO DE BARRAS (POR AÑO) ---
elif menu == "📊 Sismos por Año":
    st.subheader("📊 Número de sismos por año")
    conteo = df_filtrado["año"].value_counts().sort_index()
    
    fig_bar = px.bar(
        x=conteo.index,
        y=conteo.values,
        labels={"x": "Año", "y": "Número de sismos"},
        color=conteo.values,
        color_continuous_scale="Viridis",
        title="Frecuencia de sismos por año"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- HISTOGRAMA DE MAGNITUDES ---
elif menu == "📈 Distribución de Magnitudes":
    st.subheader("📈 Distribución de magnitudes sísmicas")
    fig_hist = px.histogram(
        df_filtrado,
        x="magnitud",
        nbins=25,
        title="Distribución de magnitudes en el rango seleccionado",
        color_discrete_sequence=["#FF4B4B"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# --- RELACIÓN MAGNITUD VS PROFUNDIDAD ---
elif menu == "📉 Relación Magnitud–Profundidad":
    st.subheader("📉 Relación entre Magnitud y Profundidad")
    fig_scatter = px.scatter(
        df_filtrado,
        x="profundidad",
        y="magnitud",
        color="magnitud",
        color_continuous_scale="Turbo",
        hover_data=["fecha", "magnitud", "profundidad"],
        title="Correlación entre magnitud y profundidad"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Datos: Instituto Geofísico EPN | Catálogo Nacional de Sismos 2012–2025")
