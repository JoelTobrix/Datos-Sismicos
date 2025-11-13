# Imagen base oficial de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements-api.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements-api.txt

# Copiar todo el proyecto al contenedor
COPY . .

# Exponer el puerto donde correrá la API
EXPOSE 8000

# Comando para ejecutar la API
CMD ["uvicorn", "scripts.api:app", "--host", "0.0.0.0", "--port", "8000"]

RUN apt-get update && apt-get install -y libgomp1


RUN pip install --no-cache-dir -r requirements-api.txt

