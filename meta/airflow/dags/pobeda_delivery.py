
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

with DAG(
    dag_id="pobeda_delivery",
    schedule=None,
    catchup=False,
    dagrun_timeout=dt.timedelta(minutes=60),
    tags=["pobeda", "delivery"],
    default_args=default_args,
) as dag:
    ftp_2_s3 = BashOperator(
        task_id="ftp_2_s3",
        bash_command="""
            apt-get update \
            && apt-get install iputils-ping -y \
            && curl https://dl.min.io/client/mc/release/linux-amd64/mc --create-dirs -o $HOME/minio-binaries/mc \
            && chmod +x $HOME/minio-binaries/mc \
            && export PATH=$PATH:$HOME/minio-binaries/ \
            && mc alias set myminio http://minio:9001/ admin admin123 \
            && cd /srv/ \
            && wget -m ftp://mm-bav:XRbTMp2N@95.68.243.12:/Upload/delivery_20221114.csv \
            && cd /srv/95.68.243.12/Upload \
            && mc cp delivery_20221114.csv myminio/data-science/delivery_20221114.csv
        """,
        dag=dag,
    )

    transform = BashOperator(
        task_id="transform",
        bash_command='echo "transform"',
        dag=dag,
    )

    validate = BashOperator(
        task_id="validate",
        bash_command='echo "validate"',
        dag=dag,
    )

    s3_2_db = BashOperator(
        task_id="s3_2_db",
        bash_command='echo "s3_2_db"',
        dag=dag,
    )

    validate_db = BashOperator(
        task_id="validate_db",
        bash_command='echo "validate_db"',
        dag=dag,
    )

    ftp_2_s3 >> transform >> validate >> s3_2_db >> validate_db
