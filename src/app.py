import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns


url = "https://companies-market-cap-copy.vercel.app/index.html"

res = requests.get(url)

if res.status_code == 200:
    sopa = BeautifulSoup(res.text, 'html.parser')
    
    tablas = sopa.find_all("table")
    
    tabla = tablas[0]
    
    filas = tabla.find_all("tr")
    
    encabezados = []
    for th in filas[0].find_all("th"):
        encabezados.append(th.get_text(strip=True))
    
    datos = []
    for fila in filas[1:]:
        celdas = fila.find_all("td")
        fila_datos = []
        for celda in celdas:
            fila_datos.append(celda.get_text(strip=True))
        datos.append(fila_datos)
    
    df = pd.DataFrame(datos, columns=encabezados)
    
    for columna in df.columns:
        df[columna] = df[columna].str.replace("$", "", regex=False)
        df[columna] = df[columna].str.replace("B", "", regex=False)
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
    
    df_limpio = df.dropna()
    
    df_limpio.reset_index(drop=True, inplace=True)
    
    conexion = sqlite3.connect('crecimiento_empresas.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crecimiento_anual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anio INTEGER,
            crecimiento REAL
        )
    ''')
    
    for index, fila in df_limpio.iterrows():
        cursor.execute('''
            INSERT INTO crecimiento_anual (anio, crecimiento) 
            VALUES (?, ?)
        ''', (fila[0], fila[1]))
    
    conexion.commit()
    
    conexion.close()
    
    print("\nListo. Se guardaron los datos en la base de datos.")
else:
    print(f"F en el chat. Código de error: {res.status_code}")

