# Imagen base liviana con Python 3.10
FROM python:3.10-slim

# Directorio principal
WORKDIR /app

# Dependencias necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias Python sin caché
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el resto de archivos
COPY . .

# Railway definirá automáticamente $PORT
EXPOSE 8080

# Iniciar FastAPI usando el puerto de Railway
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
