from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'asavinkov',
    'depends_on_past': False,
    'retries': 10,
    'concurrency': 1
}

# dag declaration

dag = DAG(
    dag_id="test_dag",
    default_args=default_args,
    start_date=datetime(2022, 12, 12),
    schedule_interval=timedelta(days=1)
)



bash_task1 = BashOperator(task_id='bash_task_1',
                         bash_command="echo 'Hello Airflow!'",
                         dag=dag)

bash_task2 = BashOperator(task_id='bash_task_2',
                         bash_command="echo 'Hello Airflow!'",
                         dag=dag)

bash_task1 >> bash_task2
