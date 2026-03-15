import os
import json
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 1. Tickers del IBEX 35 (Componentes actuales con el sufijo .MC)
tickers_ibex = [
    "ANA.MC", "ACX.MC", "ACS.MC", "AENA.MC", "AMS.MC", "MTS.MC", "SAB.MC", 
    "SAN.MC", "BKT.MC", "BBVA.MC", "CABK.MC", "CLNX.MC", "ENG.MC", "ELE.MC", 
    "FER.MC", "FLUI.MC", "GRF.MC", "IAG.MC", "IBE.MC", "ITX.MC", "IDR.MC", 
    "COL.MC", "LOG.MC", "MAP.MC", "MEL.MC", "MRL.MC", "NAT.MC", "PUIG.MC", 
    "REE.MC", "REP.MC", "ROVI.MC", "SCYR.MC", "SLBA.MC", "TEF.MC", "UNI.MC"
]

data_ibex = {}
if not os.path.exists('data'):
    os.makedirs('data')
for ticker in tqdm(tickers_ibex):
    try:
        accion = yf.download(ticker, start='2020-01-01', end='2021-01-01', progress=False)
        
        if not accion.empty:
            # Formatear datos
            accion = accion.reset_index()
            accion['Date'] = accion['Date'].dt.strftime('%Y-%m-%d')
            accion_json = accion.to_json(orient='records')
            data_ibex[ticker] = json.loads(accion_json)
        else:
            print(f"Sin datos para {ticker}")

    except Exception as e:
        print(f"Error en {ticker}: {e}")
with open("data/json_ibex35.json", "w", encoding="utf-8") as bolsa_ibex:
    json.dump(data_ibex, bolsa_ibex, indent=4, ensure_ascii=False)