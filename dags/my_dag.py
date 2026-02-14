from airflow import DAG
from datetime import datetime
import pytz
import requests
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
import os
import pandas as pd

import psycopg2
from psycopg2 import sql

from sqlalchemy import create_engine



load_dotenv("../.env")  # Lädt die .env-Datei
api_key = os.getenv("TANKERKOENIG_API_KEY")
db_password = os.getenv("DB_PASSWORD")
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

    ti  = context['ti']  # Task instance um XCOM zu verwenden
    data = ti.xcom_pull(key="api_response", task_ids="get_data")  # Holt die API-Antwort aus XCom

    if not data:
        print("Keine Daten gefunden in XCom")
        return None

    tankstellen = data["stations"]  # Extrahiert die Liste der Tankstellen aus der API-Antwort
    df = pd.DataFrame(tankstellen)

    df["retrieval_time"] = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%H:%M")
    df["retrieval_date"] = datetime.now().date()


    engine = create_engine(
        f"postgresql+psycopg2://postgres:{db_password}@10.70.112.3/gasstation-db")

    # Verbindung zu Google Cloud SQL
    #conn = psycopg2.connect(
    #    host="10.70.112.3",                 # IP SQL-Instance
    #    database="gasstation-db",           # DB Name
    #    user="postgres",                    # Username
    #    password=os.getenv("DB_PASSWORD")   # Password aus .env
    #)

    df_tankstellen = df[["id", "name", "brand", "street", "place", "lat", "lng", "dist", "houseNumber", "postCode"]]
    df_abfragen = df[["id", "diesel", "e5", "e10", "isOpen","retrieval_time", "retrieval_date"]]
    df_abfragen = df_abfragen.rename(columns={"id": "tankstellen_id", "isOpen": "isopen"})  # Umbenennen der Spalten für 
    die Abfragen-Tabelle
    
    df_abfragen.to_sql(
        "abfragen", 
        engine, 
        index=False)  

    df_tankstellen.to_sql(
        "tankstellen", 
        engine, 
        if_exists="append", 
        index=False)

    #conn.close()  # Verbindung schließen

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