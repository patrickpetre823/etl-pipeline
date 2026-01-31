from airflow import DAG
from datetime import datetime
import requests
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv("../.env")  # Lädt die .env-Datei
api_key = os.getenv("TANKERKOENIG_API_KEY")
print("API-Key geladen:", api_key is not None)  # Sollte True sein

def get_data():
    
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat=48.775&lng=9.172&rad=10&sort=dist&type=all&apikey={api_key}"
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        print("Daten erfolgreich abgerufen")
        return response.json() 
    else:
        return f"Fehler: {response.status_code}"
    
def make_df():

    data = get_data()
    tankstellen = data["stations"]
    print("Tankstellen-Daten:", tankstellen)

    df = pd.DataFrame(tankstellen)
    print("DataFrame erstellt: Header", df.head()) 
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