import pandas as pd
from fastapi import FastAPI, Query
from datetime import date
import os

app = FastAPI()

# Cargar los datos al iniciar la API
RUTA_PROCESADA = os.path.join(os.path.dirname(__file__), "..", "data", "processed_catalogo.csv")

try:
    # Carga el catálogo PROCESADO 
    df_sismos = pd.read_csv(RUTA_PROCESADA)
    df_sismos['time_value'] = pd.to_datetime(df_sismos['time_value'])
    print("API: Datos procesados cargados exitosamente.")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo procesado en {RUTA_PROCESADA}.")
    print("Asegúrate de ejecutar 'python main.py' para generar 'processed_catalogo.csv'.")
    df_sismos = pd.DataFrame() # Crear un DataFrame vacío para evitar errores

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
    # Se usa .value para obtener el valor de la fecha del objeto date de Python
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # Filtrar por fechas y magnitud
    filtro_fecha = (df_sismos['time_value'] >= start_dt) & (df_sismos['time_value'] <= end_dt)
    filtro_magnitud = df_sismos['magnitude_value_P'] >= min_magnitude

    # Aplicar filtros
    df_filtrado = df_sismos[filtro_fecha & filtro_magnitud]

    # Devolver resultados como JSON
    # Se limita el número de columnas para una respuesta más ligera (opcional)
    columnas_api = ['event', 'time_value', 'latitude_value', 'longitude_value', 
                    'depth_value', 'magnitude_value_P', 'categoria_magnitud', 'categoria_profundidad']
                    
    return df_filtrado[columnas_api].to_dict(orient='records')

# --- Endpoint  categorías  ---
@app.get("/sismos/categories")
def get_categories_count(group_by: str = Query("magnitud", description="Agrupar por 'magnitud' o 'profundidad'")):
    """
    Devuelve la frecuencia de sismos por la categoría especificada.
    """
    if df_sismos.empty:
        return {"error": "Datos no cargados. Verifique el log de la API."}
        
    group_col = None
    if group_by.lower() == "magnitud":
        group_col = 'categoria_magnitud'
    elif group_by.lower() == "profundidad":
        group_col = 'categoria_profundidad'
    else:
        return {"error": "Parámetro 'group_by' inválido. Use 'magnitud' o 'profundidad'."}

    # Calcular la frecuencia de cada categoría
    df_counts = df_sismos[group_col].value_counts().reset_index()
    df_counts.columns = ['categoria', 'conteo']

    return df_counts.to_dict(orient='records')

@app.get("/sismos/region")
def get_sismos_por_region():
    """
    Devuelve el número de sismos agrupados por región o provincia.
    Si no existe una columna de región, genera agrupación ficticia según latitud.
    """
    if df_sismos.empty:
        return {"error": "Datos no cargados. Verifique el log de la API."}

    # Detectar columna de región si existe
    posibles_columnas = ['region', 'provincia', 'zona']
    col_region = next((col for col in posibles_columnas if col in df_sismos.columns), None)

    if col_region:
        df_region = df_sismos[col_region].value_counts().reset_index()
        df_region.columns = ['region', 'conteo']
    else:
        # Agrupar por latitud aproximada (norte/centro/sur del Ecuador)
        def clasificar_zona(lat):
            if lat >= -0.5:
                return "Norte"
            elif lat >= -2.5:
                return "Centro"
            else:
                return "Sur"

        df_sismos['zona'] = df_sismos['latitude_value'].apply(clasificar_zona)
        df_region = df_sismos['zona'].value_counts().reset_index()
        df_region.columns = ['region', 'conteo']

    
    return df_region.to_dict(orient='records')
   