
from __future__ import annotations

import datetime as dt

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'asavinkov',
    'depends_on_past': False,
    'start_date': dt.datetime(2022, 11, 17),
    'email': ['asavinkov@workestra.ai.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

current_date = '20221125'

with DAG(
    dag_id="pobeda_purchases",
    schedule=None,
    catchup=False,
    dagrun_timeout=dt.timedelta(minutes=60),
    tags=["pobeda", "purchases"],
    default_args=default_args,
) as dag:
    ftp_2_s3 = BashOperator(
        task_id="ftp_2_s3",
        bash_command=f"""
            mc alias set myminio http://minio:9001/ admin admin123 \
            && cd /srv/ \
            && wget -m ftp://mm-bav:XRbTMp2N@95.68.243.12:/Upload/purchases_{current_date}.csv \
            && cd /srv/scheduler_ml \
            && python setup.py develop \
            && python cli.py ftp-2-s3 --filename=purchases_{current_date}.csv --config-name=pobeda_purchases""",
        dag=dag)

    extractor = BashOperator(
        task_id="extractor",
        bash_command="cd /srv/scheduler_ml && python setup.py develop && python cli.py extractor --config-name=pobeda_purchases",
        dag=dag)

    minio_2_postgres = BashOperator(
        task_id="minio_2_postgres",
        bash_command=f"cd /srv/scheduler_ml && python setup.py develop && python cli.py minio-2-postgres --date={current_date} --config-name=pobeda_purchases",
        dag=dag)

    ftp_2_s3 >> extractor >> minio_2_postgres
