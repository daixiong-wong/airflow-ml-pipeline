import os
from datetime import datetime
from pathlib import Path

import great_expectations as gx
import numpy as np
import pandas as pd
# DAG and task decorators for interfacing with the TaskFlow API
from airflow.decorators import (
    dag,
    task,
)
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from great_expectations_provider.operators.great_expectations import (
    GreatExpectationsOperator,
)
from scipy.stats import linregress

@dag(
    schedule_interval="@daily",
    start_date=datetime(2022, 1, 1),
    catchup=False,
    default_args={
        # If the task fails, it will retry n times
        "retries": 2,  
    },
    tags=["dynamic_dag__model_train"],
)
def {{ dag_name }}():
    vendor_name = "easy_destiny"
    start_task = DummyOperator(task_id="start")

    data_quality_task = GreatExpectationsOperator(
        task_id="data_quality",
        data_context_root_dir="./dags/gx",

        data_asset_name="train_easy_destiny",
        dataframe_to_validate=pd.read_parquet(
            f"s3://{Variable.get('bucket_name')}/work_zone/data_science_project/datasets/"
            f"{vendor_name}/train.parquet"
        ),
        
        execution_engine="PandasExecutionEngine",
        expectation_suite_name=f"de-expectation-suite",

        return_json_dict=True,

        fail_task_on_validation_failure=True,
    )

    @task
    def train_and_evaluate(bucket_name: str, vendor_name: str):
        datasets_path = (
            f"s3://{bucket_name}/work_zone/data_science_project/datasets"
        )

        train = pd.read_parquet(f"{datasets_path}/{vendor_name}/train.parquet")
        test = pd.read_parquet(f"{datasets_path}/{vendor_name}/test.parquet")

        X_train = train[["distance"]].to_numpy()[:, 0]
        X_test = test[["distance"]].to_numpy()[:, 0]

        y_train = train[["trip_duration"]].to_numpy()[:, 0]
        y_test = test[["trip_duration"]].to_numpy()[:, 0]

        model = linregress(X_train, y_train)

        y_pred_test = model.slope * X_test + model.intercept
        performance = np.sqrt(np.average((y_pred_test - y_test) ** 2))
        print("--- performance RMSE ---")
        print(f"test: {performance:.2f}")
        
        return performance

    def _is_deployable(ti):
        performance = ti.xcom_pull(task_ids="train_and_evaluate")

        if performance < 500:
            print(f"is deployable: {performance}")
            return "deploy"
        else:
            print("is not deployable")
            return "notify"

    is_deployable_task = BranchPythonOperator(
        task_id="is_deployable",

        python_callable=_is_deployable,
        
        do_xcom_push=False,
    )

    @task
    def deploy():
        print("Deploying...")

    @task
    def notify(message):
        print(f"{message}. " "Notify to mail: admin@easy_destiny.com")

    end_task = DummyOperator(task_id="end", trigger_rule="none_failed_or_skipped")

    (
        start_task
        >> data_quality_task
        >> train_and_evaluate(
            bucket_name="{{ var.value.bucket_name }}",
            vendor_name="easy_destiny",
        )
        >> is_deployable_task
        >> [deploy(), notify("Not deployed")]
        >> end_task
    )

dag_{{ dag_name }} = {{ dag_name }}()
