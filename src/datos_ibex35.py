import os
import json
import yfinance as yf
from config import ACCESS_TOKEN
import pandas as pd
import numpy as np
from tqdm import tqdm


# Tickers del IBEX 35 (formato Yahoo Finance: símbolo + .MC para Mercado Continuo de Madrid)
tickers = [
    "ACS.MC",    # ACS, Actividades de Construcción y Servicios
    "ACX.MC",    # Acerinox
    "AENA.MC",   # Aena
    "AMS.MC",    # Amadeus IT Group
    "ANA.MC",    # Acciona
    "ANE.MC",    # Corporación Acciona Energías Renovables
    "BBVA.MC",   # Banco Bilbao Vizcaya Argentaria
    "BKT.MC",    # Bankinter
    "CABK.MC",   # CaixaBank
    "CLNX.MC",   # Cellnex Telecom
    "COL.MC",    # Inmobiliaria Colonial
    "ELE.MC",    # Endesa
    "ENG.MC",    # Enagás
    "FDR.MC",    # Fluidra
    "FER.MC",    # Ferrovial
    "GRF.MC",    # Grifols
    "IAG.MC",    # International Airlines Group
    "IBE.MC",    # Iberdrola
    "IDR.MC",    # Indra Sistemas
    "ITX.MC",    # Inditex
    "LOG.MC",    # Logista
    "MAP.MC",    # MAPFRE
    "MEL.MC",    # Meliá Hotels International
    "MRL.MC",    # Merlin Properties
    "MTS.MC",    # ArcelorMittal
    "NTGY.MC",   # Naturgy Energy Group
    "RED.MC",    # Redeia (Red Eléctrica)
    "REP.MC",    # Repsol
    "SAB.MC",    # Banco de Sabadell
    "SAN.MC",    # Banco Santander
    "SCYR.MC",   # Sacyr
    "SLR.MC",    # Solaria Energía y Medio Ambiente
    "TEF.MC",    # Telefónica
    "UNI.MC",    # Unicaja Banco
    "VIS.MC",    # Viscofan
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

with open("data/json/json_ibex35.json", "w", encoding="utf-8") as bolsa35:
    json.dump(data_ibex35, bolsa35, indent=4, ensure_ascii=False)
