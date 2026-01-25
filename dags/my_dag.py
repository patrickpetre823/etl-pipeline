from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator

def hello_world():
    print("Hello, World!")


with DAG(
    "my_dag", 
    start_date=datetime(2025, 1, 25),
    schedule="@daily",
    catchup=False
):
    PythonOperator(
        task_id="my_task",
        python_callable=hello_world
        )
    