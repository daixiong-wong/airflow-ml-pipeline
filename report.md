## Building an Advanced Data Pipeline With Data Quality Checks

This report documents the development of an advanced data pipeline using Apache Airflow. 
The project aims to establish a robust framework that incorporates data quality checks, dynamic DAGs, and machine learning model training and evaluation. 
The pipeline leverages tools like Great Expectations and the TaskFlow API to ensure efficient and scalable workflows.

### 1. The DAG Details

#### Overview of Tasks:
Descriptions of the tasks that constitute the DAG:
- `start`: an empty task marking the start of the DAG. It doesn't include any behavior.
- `data_quality`: triggers a data quality check on the data using the `@task.virtualenv` decorator from the TaskFlow API.
- `train_and_evaluate`: trains and evaluates a model to estimate ride duration and returns the performance metric.
- `is_deployable`: decides whether to deploy a model based on the model performance.
- `deploy`: prints a deployment message to simulate the deployment process of the model.
- `notify`: prints a notification message to simulate the notification for a low-performance model.
- `end`: an empty task marking the end of the DAG. It doesn't include any behavior and will be executed with the DummyOperator.

---

### 2. Setting Up Airflow's Components

---

### 3. Preprocessing the Data

The data was preprocessed and divided into train and test sets, partitioned by vendor name. 
The `data` folder structure is organized as follows:

Structure of the data folder
- `"work_zone/data_science_project/datasets/<VENDOR_NAME>/train.parquet"`
- `"work_zone/data_science_project/datasets/<VENDOR_NAME>/train.parquet"`

Where `<VENDOR_NAME>` includes:
- `easy_destiny`
- `alitran`
- `to_my_place_ai`

#### Synchronizing Data with *Raw Data Bucket*

To store the data in the Raw Data Bucket, the following commands were executed:

```bash
cd data
aws s3 sync work_zone s3://<RAW-DATA-BUCKET>/work_zone/
cd ..
```

Next steps include designing a pipeline to validate the quality of this data and building custom models for each vendor based on specific requirements.

---

### 4. Creating the DAG and Its Tasks

#### Checking Data Quality

Data quality checks ensure the suitability of the data for its intended purpose. 
Validation of the `passenger_count` column was performed using **Great Expectations** (GX) to meet the business rule that no trip can have more than 6 passengers. 
Models were only trained if this criterion was satisfied.

#### Training and Evaluating the ML Model

The pipeline includes a task to train a **linear regression model** for predicting trip duration, followed by performance evaluation using **Root-Mean-Square Error (RMSE)**. 
The TaskFlow API was used to configure this task, ensuring the performance metric was returned for subsequent tasks.

#### Branching the ML Model

Conditional task execution was implemented using the `BranchPythonOperator`. 
Depending on model performance, the pipeline either proceeded to deploy the model or triggered a notification for low performance, ensuring adaptability in different scenarios.

#### Defining the DAG Dependencies

Task dependencies were established using the `>>` operator, creating a seamless execution flow: 

---

### 5. Dynamic DAGs

#### Avoiding Code Duplication

To enhance scalability and maintainability, dynamic DAGs were implemented. 
The approach eliminated repetitive code by using Jinja templates to generate DAGs with configurable parameters.

#### Creating the Template File

The DAG script was modified to use Jinja templates, replacing hardcoded values like DAG name (`model_trip_duration_easy_destiny`) 
and vendor name (`easy_destiny`) with placeholders (`{{ dag_name }}` and `{{ vendor_name }}`).

#### Creating the Configuration Files

JSON configuration files were created to specify template variables for each DAG.

- config_easy_destiny.json
  
  ```JSON
  {
  "dag_name": "model_trip_duration_easy_destiny",
  "vendor_name": "easy_destiny"
  }
  ```

Similar configurations were created for `alitran` and `to_my_place_ai`.

#### Generating the DAGs

With the template and configurations ready, the following command was used to generate the DAGs dynamically.

```bash
cd src/templates
python3 ./generate_dags.py
```

The generated DAGs were stored in the `src/dags/` folder.

---

### 6. Running the DAGs with Airflow

The DAGs folder was synchronized with the DAGs Bucket using:

```bash
cd ../..
aws s3 sync src/dags s3://<DAGS-BUCKET>/dags
```

After refreshing the Airflow UI, the DAGs were toggled and executed. The results were as follows:

- **model_trip_duration_alitran**: it will notify the model was not deployed.
- **model_trip_duration_easy_destiny**: it will deploy the model.
- **model_trip_duration_to_my_place_ai**: it will fail the checkpoint in Great Expectations.

---

### Reflections and Improvements

This project demonstrates the successful integration of data quality checks, dynamic DAG generation, and ML model training in Apache Airflow. 
Future improvements could include:

- Exploring advanced data validation techniques.
- Optimizing pipeline performance for larger datasets.
- Integrating more complex branching logic for additional workflows.

The project establishes a strong foundation for building scalable and efficient data pipelines while adhering to industry best practices.




