FROM python:3.10-slim

WORKDIR /app

# Dependencias necesarias para OpenCV (imprescindibles en Railway)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . .

# Railway detecta el puerto 8080 automáticamente
EXPOSE 8080

# Ejecutar la app en 0.0.0.0:8080 (NECESARIO)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
