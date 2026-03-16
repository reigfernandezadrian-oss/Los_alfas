import json
import pandas as pd
import os


# Cargar el JSON con los datos del IBEX 35
with open("data/json/json_ibex35.json", "r", encoding="utf-8") as f:
    data_ibex35 = json.load(f)

# Aplanar el JSON: cada ticker tiene una lista de registros con columnas MultiIndex
# Las claves del JSON tienen formato: "('Date', '')", "('Close', 'TICKER')", etc.
filas = []
for ticker, registros in data_ibex35.items():
    for registro in registros:
        fila = {"Ticker": ticker}
        for clave, valor in registro.items():
            # Extraer el nombre de la columna del formato MultiIndex "('ColName', 'TICKER')"
            if clave.startswith("("):
                # Parsear la tupla: "('Date', '')" o "('Close', 'ACS.MC')"
                partes = clave.strip("()").split(",")
                nombre_col = partes[0].strip().strip("'\"")
                fila[nombre_col] = valor
            else:
                fila[clave] = valor
        filas.append(fila)

# Crear DataFrame
df = pd.DataFrame(filas)

# Ordenar columnas: Ticker y Date primero, luego las demás
columnas_orden = ["Ticker", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
# Filtrar solo las columnas que existan en el DataFrame
columnas_presentes = [col for col in columnas_orden if col in df.columns]
# Añadir columnas extra que no estén en el orden predefinido
columnas_extra = [col for col in df.columns if col not in columnas_orden]
df = df[columnas_presentes + columnas_extra]

# Convertir tipos
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Eliminar filas donde todos los valores de precio sean NaN
columnas_precio = ["Open", "High", "Low", "Close", "Adj Close"]
columnas_precio_presentes = [col for col in columnas_precio if col in df.columns]
if columnas_precio_presentes:
    df = df.dropna(subset=columnas_precio_presentes, how="all")

# Ordenar por Ticker y Date
df = df.sort_values(by=["Ticker", "Date"]).reset_index(drop=True)

# Guardar como CSV
df.to_csv("data/clean_Excel/clean_ibex35.csv", index=False, encoding="utf-8")

print(f"CSV limpio guardado en data/clean_Excel/clean_ibex35.csv")
print(f"Total de filas: {len(df)}")
print(f"Tickers encontrados: {df['Ticker'].nunique()}")
print(f"\nPrimeras filas:")
print(df.head(10))

# Guardar como xlsx
df.to_csv("data/clean_Excel/clean_ibex35.xlsx", index=False, encoding="utf-8")

print(f"CSV limpio guardado en data/clean_Excel/clean_ibex35.xlsx")
print(f"Total de filas: {len(df)}")
print(f"Tickers encontrados: {df['Ticker'].nunique()}")
print(f"\nPrimeras filas:")
print(df.head(10))
