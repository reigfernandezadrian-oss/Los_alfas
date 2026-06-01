# 1ºUsa Python como base
FROM python:3.9-slim

# 2ºDirectorio de trabajo en el contenedor
WORKDIR /app

# 3ºCopia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4ºCORRECCIÓN: Copia todo el contenido del proyecto (data, src, etc.)
COPY . .

# 5ºComando de ejecución
CMD ["python", "-m", "streamlit", "run", "web/Inicio.py"]