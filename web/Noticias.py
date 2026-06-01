import os
import json
import yfinance as yf
from config import ACCESS_TOKEN
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime
from datos_ibex35 import tickers as tikers1
from datos_sp500 import tickers as tikers2
todotikers = tikers1 + tikers2
try:
    for accion in todotikers:
        ticker_obj = yf.Ticker(accion)
        noticias_completas = ticker_obj.news
        noticias_recientes = noticias_completas[:2]

        with open("data/json/news.json", "a", encoding= "utf-8") as noticias:
            json.dump(noticias_recientes,noticias,indent=4,ensure_ascii=False)

except Exception as e:
    print(f"Error en {todotikers}: {e}")