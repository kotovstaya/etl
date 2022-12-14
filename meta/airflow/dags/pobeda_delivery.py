
from __future__ import annotations

import datetime as dt

import pendulum
from airflow import DAG
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

SLACK_CONN_ID = 'slack'
def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed.
            <@U022T50D4F5>  
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *gsutil URI*: {gsutil_URI} 
            """.format(
                task=context.get('task_instance').task_id,
                dag=context.get('task_instance').dag_id,
                ti=context.get('task_instance'),
                exec_date=context.get('execution_date'),
                gsutil_URI=context.get('task_instance').log_url.replace("8080", "8082")
            )

    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return failed_alert.execute(context=context)


default_args = {
    'owner': 'asavinkov',
    'depends_on_past': False,
    'start_date': dt.datetime(2022, 11, 17),
    'email': ['asavinkov@workestra.ai.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': dt.timedelta(seconds=5),
    'on_failure_callback': task_fail_slack_alert,
}

current_date = Variable.get("dt")

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
        bash_command=f"""
            mc alias set myminio http://minio:9001/ admin admin123 \
            && cd /srv/ \
            && wget -m ftp://mm-bav:XRbTMp2N@95.68.243.12:/Upload/delivery_{current_date}.csv \
            && cd /srv/scheduler_ml \
            && python setup.py develop \
            && python cli.py ftp-2-s3 --filename=delivery_{current_date}.csv --config-name=pobeda_delivery""",
        dag=dag)

    extractor = BashOperator(
        task_id="extractor",
        bash_command="cd /srv/scheduler_ml && python setup.py develop && python cli.py extractor --config-name=pobeda_delivery",
        dag=dag)

    minio_2_postgres = BashOperator(
        task_id="minio_2_postgres",
        bash_command=f"cd /srv/scheduler_ml && python setup.py develop && python cli.py minio-2-postgres --date={current_date} --config-name=pobeda_delivery",
        dag=dag)

    ftp_2_s3 >> extractor >> minio_2_postgres 
