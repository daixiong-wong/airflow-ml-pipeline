---

# Building an Advanced Data Pipeline With Data Quality Checks

This project demonstrates the development of an advanced data pipeline to support a Machine Learning team. The goal is to create a pipeline for three fictitious Mobility-As-A-Service vendors—**Alitran**, **Easy Destiny**, and **ToMyPlaceAI**—to preprocess and validate data, train machine learning models, and evaluate their deployment suitability based on key metrics. By continuously training and assessing the models, each vendor can improve their ride duration estimation services.

---

## Overview

### DAG Details
This project involves implementing an Apache Airflow Directed Acyclic Graph (DAG) to automate the following tasks:
- Validate data
- Train and evaluate an ML model
- Decide whether to deploy the model or notify stakeholders of low performance.

The DAG is generalized as a template to dynamically generate workflows for different vendors.

The DAG structure used for this project is illustrated below:

![DAG Diagram](img/dag-diagram)

### Setting Up Airflow's Components
The Airflow setup includes:
- Launching an AWS EC2 instance
- Configuring security groups and key pairs
- Installing necessary Airflow dependencies
- Creating an Airflow user and initializing the environment
- Launching the Airflow scheduler, metadata database, and webserver to manage DAG execution.

### Preprocessing the Data
The data for this project is preprocessed and partitioned by vendor name. It is further divided into training and testing datasets stored as parquet files. 
These splits will be used to train and evaluate a machine learning model in the Work Zone of the Raw Data Bucket.

### Creating the DAG and Its Tasks

- **Checking Data Quality**:  
  Ensuring the data meets the required standards using **Great Expectations (GX)** to validate key quality dimensions, such as accuracy, completeness, consistency, and 
  validity.

- **Training and Evaluating the ML Model**:  
  Using the TaskFlow API to train a linear regression model that predicts ride durations. The model's performance is measured using Root Mean Square Error (RMSE) on the test
  data. The task is configured to return performance metrics for decision-making.

- **Branching the ML Model**:  
  Introducing conditional task execution with the `BranchPythonOperator` to control the DAG flow. Based on the evaluation results, tasks dynamically branch to deploy the model 
  or notify stakeholders.

- **Defining DAG Dependencies**:  
  Establishing task relationships for smooth execution, where dependencies are explicitly declared using the `>>` operator.

### Dynamic DAGs
Dynamic DAG generation enables scaling and customization for multiple vendors:
- Template files define a common workflow structure.
- Configuration files provide vendor-specific details.
- The Airflow scheduler programmatically generates and executes vendor-specific DAGs.

### Running the DAGs with Airflow
The final step involves deploying and running the DAGs on the Airflow webserver. This includes:
- Monitoring task execution and logs through the Airflow UI.
- Addressing issues and optimizing the workflow based on observed performance.

## Conclusion
This project integrates best practices in data engineering and machine learning workflow automation. It highlights the use of **Apache Airflow**, **Great Expectations**, and **AWS infrastructure** to create scalable, reliable, and dynamic pipelines for data quality validation and machine learning model deployment.

---
