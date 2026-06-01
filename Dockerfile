FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python src/datos_sp500.py
RUN python src/datos_ibex35.py

CMD ["streamlit", "run", "web/Inicio.py"]
