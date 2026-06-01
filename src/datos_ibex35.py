import os
import json
import yfinance as yf
from config import ACCESS_TOKEN
import pandas as pd
import numpy as np
from tqdm import tqdm


tickers = [
    "ACS.MC",
    "ACX.MC",
    "AENA.MC",
    "AMS.MC",
    "ANA.MC",
    "ANE.MC",
    "BBVA.MC",
    "BKT.MC",
    "CABK.MC",
    "CLNX.MC",
    "COL.MC",
    "ELE.MC",
    "ENG.MC",
    "FDR.MC",
    "FER.MC",
    "GRF.MC",
    "IAG.MC",
    "IBE.MC",
    "IDR.MC",
    "ITX.MC",
    "LOG.MC",
    "MAP.MC",
    "MEL.MC",
    "MRL.MC",
    "MTS.MC",
    "NTGY.MC",
    "RED.MC",
    "REP.MC",
    "SAB.MC",
    "SAN.MC",
    "SCYR.MC",
    "SLR.MC",
    "TEF.MC",
    "UNI.MC",
    "VIS.MC",
]

data_ibex35 = {}

for ticker in tqdm(tickers):
    try:
        accion = yf.download(ticker, start='2020-01-01', end='2025-01-01', progress=False)

        if not accion.empty:
            accion = accion.reset_index()
            accion['Date'] = accion['Date'].dt.strftime('%Y-%m-%d')
            accion_json = accion.to_json(orient='records')
            data_ibex35[ticker] = json.loads(accion_json)
        else:
            print(f"Sin datos para {ticker}")

    except Exception as e:
        print(f"Error en {ticker}: {e}")

with open("data/json_ibex35.json", "w", encoding="utf-8") as bolsa35:
    json.dump(data_ibex35, bolsa35, indent=4, ensure_ascii=False)
