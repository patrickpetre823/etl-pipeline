from airflow import DAG
from datetime import datetime
import pytz
import requests
from airflow.providers.standard.operators.python import PythonOperator
from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3

load_dotenv("../.env")  # Lädt die .env-Datei
api_key = os.getenv("TANKERKOENIG_API_KEY")
print("API-Key geladen:", api_key is not None)  # Sollte True sein

def get_data(**context):

    ti = context['ti']       # Task instance um XCOM zu verwenden
    
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat=48.775&lng=9.172&rad=10&sort=dist&type=all&apikey={api_key}"
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        ti.xcom_push(key="api_response", value=response.json())  # Speichert die API-Antwort in XCom
        return response.json() 
    else:
        return f"Fehler: {response.status_code}"
    

def make_df(**context):

    # Daten aus XCom laden und in Dataframe umwandeln
    ti  = context['ti']  # Task instance um XCOM zu verwenden
    data = ti.xcom_pull(key="api_response", task_ids="get_data")  # Holt die API-Antwort aus XCom

    if not data:
        print("Keine Daten gefunden in XCom")
        return None

    gas_data = data["stations"]  # Extrahiert die Tankstellen-Daten aus der API-Antwort
    df = pd.DataFrame(gas_data)

    # Daten im Dataframe bereinigen und formatieren
    df["retrieval_time"] = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%H:%M")   # Fügt die aktuelle Uhrzeit hinzu
    df["retrieval_date"] = datetime.now().date()                                            # Fügt das aktuelle Datum hinzu

    df["e5"] = df["e5"].replace(None, 0).astype(float)  # Ersetzt None-Werte in der Spalte "e5" durch 0 und konvertiert in float (sollte bereits float sein, aber sicherheitshalber)
    df["e10"] = df["e10"].replace(None, 0).astype(float)  
    df["diesel"] = df["diesel"].replace(None, 0).astype(float)  

    # Write to database
    conn = sqlite3.connect("/opt/airflow/dags/tankstellen.db")
    df.to_sql("tankstellen", conn, if_exists="append", index=False)
    historische_daten = pd.read_sql('SELECT e5 FROM tankstellen', conn)
    print(historische_daten)
    conn.close()

    return df



with DAG(
    "my_dag", 
    start_date=datetime(2025, 1, 25),
    schedule="5 * * * *",
    catchup=False) as dag:

    task_get_data = PythonOperator(
        task_id="get_data",
        python_callable=get_data
        )
    
    task_make_df = PythonOperator(
        task_id="make_df",
        python_callable=make_df
        )

    task_get_data >> task_make_df 