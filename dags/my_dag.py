from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator

def get_data():
    url = "https://creativecommons.tankerkoenig..de/api/v4"
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        return response.json() 
    else:
        return f"Fehler: {response.status_code}"
    


with DAG(
    "my_dag", 
    start_date=datetime(2025, 1, 25),
    schedule="* * * * 5",
    catchup=False
):
    PythonOperator(
        task_id="my_task",
        python_callable=get_data
        )
    