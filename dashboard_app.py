import pandas as pd
import plotly.express as px
import streamlit as st
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor Sísmico Ecuador - Dashboard", layout="wide")

st.title("🌋 Monitor Sísmico del Ecuador")
st.markdown("Visualización interactiva de los sismos registrados entre 2012 y 2025")

# --- CARGAR DATOS (FUNCIÓN CON CACHÉ) ---

@st.cache_data
def load_data():
    ruta_datos = "data/cat_origen_2012-jul2025.txt"
    
    # Verificación de que el archivo exista antes de intentar leerlo
    if not os.path.exists(ruta_datos):
        st.error(f"Error: No se encontró el archivo de datos en la ruta esperada: {ruta_datos}. Por favor, verifica que el archivo esté en tu repositorio de GitHub.")
        return pd.DataFrame() # Retorna un DataFrame vacío para evitar errores

    # Lectura del archivo de datos
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
    
    # Eliminar filas con valores NaN en columnas críticas después del preprocesamiento
    df.dropna(subset=['fecha', 'lat', 'lon', 'magnitud', 'profundidad'], inplace=True)

    return df

df = load_data()

# Si el DataFrame está vacío debido al error de archivo, detenemos la ejecución del resto del script
if df.empty:
    st.stop()


# --- FILTROS LATERALES ---
st.sidebar.header("Filtros de visualización")

#  Calcular años_disponibles
años_disponibles = sorted(df["año"].dropna().unique().tolist())

# Manejo de años disponibles si la lista está vacía
default_años = años_disponibles[-3:] if len(años_disponibles) >= 3 else años_disponibles
if not default_años:
    default_años = [2024] # Fallback si no hay años en los datos

año_sel = st.sidebar.multiselect("Seleccionar año(s):", años_disponibles, default=default_años)

# Verificar si son rangos validos
min_mag = float(df["magnitud"].min())
max_mag = float(df["magnitud"].max())

mag_min, mag_max = st.sidebar.slider(
    "Rango de magnitud:",
    min_mag,
    max_mag,
    (min(4.0, max_mag), min(7.0, max_mag)) # Ajustar el valor por defecto
)

min_prof = float(df["profundidad"].min())
max_prof = float(df["profundidad"].max())

prof_max = st.sidebar.slider(
    "Profundidad máxima (km):",
    min_prof,
    max_prof,
    max_prof
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
    
    if not df_filtrado.empty:
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
    else:
        st.warning("No hay sismos para mostrar con los filtros seleccionados.")

# --- GRÁFICO DE BARRAS (POR AÑO) ---
elif menu == "📊 Sismos por Año":
    st.subheader("📊 Número de sismos por año")
    if not df_filtrado.empty:
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
    else:
        st.warning("No hay datos para generar el gráfico con los filtros seleccionados.")

# --- HISTOGRAMA DE MAGNITUDES ---
elif menu == "📈 Distribución de Magnitudes":
    st.subheader("📈 Distribución de magnitudes sísmicas")
    if not df_filtrado.empty:
        fig_hist = px.histogram(
            df_filtrado,
            x="magnitud",
            nbins=25,
            title="Distribución de magnitudes en el rango seleccionado",
            color_discrete_sequence=["#FF4B4B"]
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("No hay datos para generar el histograma con los filtros seleccionados.")

# --- RELACIÓN MAGNITUD VS PROFUNDIDAD ---
elif menu == "📉 Relación Magnitud–Profundidad":
    st.subheader("📉 Relación entre Magnitud y Profundidad")
    if not df_filtrado.empty:
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
    else:
        st.warning("No hay datos para generar el gráfico de dispersión con los filtros seleccionados.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Datos: Instituto Geofísico EPN | Catálogo Nacional de Sismos 2012–2025")
