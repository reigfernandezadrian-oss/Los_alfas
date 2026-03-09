import os
import json
import yfinance as yf # type: ignore
from config import ACCESS_TOKEN
import pandas as pd # type: ignore
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore




#Obtener tickers del sp500 ( las mejores empresas de eeuu, hay 500 pero usaremos estas 5 que son las mas importantes)
tickers = ["AAPL", "NVDA", "GOOGL", "AMZN", "MSFT"]

data_sp500 = {}

#with open():
for ticker in tickers:
    try:
        accion = yf.download(ticker, start='2020-01-01', end='2021-01-01')
        accion_json = accion.to_json(orient='records')
        sp500 = json.loads(accion_json)
        if sp500:
            data_sp500[ticker] = sp500
        else:
            print("Error")

    except Exception as e:
        print(f"Se a producido un error en {ticker}: {e}")

with open("data/json_sp500.json", "w", encoding= "utf-8") as bolsa500:
    json.dump(data_sp500,bolsa500,indent=4,ensure_ascii=False)











