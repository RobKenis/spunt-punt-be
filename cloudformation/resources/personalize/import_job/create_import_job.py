# Imports
import boto3
import json
import numpy as np
import pandas as pd
import time

# Configure the SDK to Personalize:
personalize = boto3.client('personalize')
personalize_runtime = boto3.client('personalize-runtime')

role_arn = 'ROLE_ARN'
dataset_group_arn = 'DATA_GROUP_ARN'
bucket = "BUCKET"
filename = "FILE"

data = pd.read_csv('u.data', sep='\t', names=['USER_ID', 'ITEM_ID', 'RATING', 'TIMESTAMP'])
pd.set_option('display.max_rows', 5)

data = data[data['RATING'] > 3]  # Keep only movies rated higher than 3 out of 5.
data = data[['USER_ID', 'ITEM_ID', 'TIMESTAMP']]  # select columns that match the columns in the schema below
data.to_csv(filename, index=False)
boto3.Session().resource('s3').Bucket(bucket).Object(filename).upload_file(filename)

schema = {
    "type": "record",
    "name": "Interactions",
    "namespace": "com.amazonaws.personalize.schema",
    "fields": [
        {
            "name": "USER_ID",
            "type": "string"
        },
        {
            "name": "ITEM_ID",
            "type": "string"
        },
        {
            "name": "TIMESTAMP",
            "type": "long"
        }
    ],
    "version": "1.0"
}

create_schema_response = personalize.create_schema(
    name="personalize-demo-schema",
    schema=json.dumps(schema)
)

schema_arn = create_schema_response['schemaArn']
print(json.dumps(create_schema_response, indent=2))

dataset_type = "INTERACTIONS"
create_dataset_response = personalize.create_dataset(
    name="spunt-video-interactions",
    datasetType=dataset_type,
    datasetGroupArn=dataset_group_arn,
    schemaArn=schema_arn
)

dataset_arn = create_dataset_response['datasetArn']
print(json.dumps(create_dataset_response, indent=2))

create_dataset_import_job_response = personalize.create_dataset_import_job(
    jobName="personalize-spunt-import1",
    datasetArn=dataset_arn,
    dataSource={
        "dataLocation": "s3://{}/{}".format(bucket, filename)
    },
    roleArn=role_arn
)

dataset_import_job_arn = create_dataset_import_job_response['datasetImportJobArn']
print(json.dumps(create_dataset_import_job_response, indent=2))

recipe_arn = 'arn:aws:personalize:::recipe/aws-personalized-ranking'
create_solution_response = personalize.create_solution(
    name="spunt-video-recommendation",
    datasetGroupArn=dataset_group_arn,
    recipeArn=recipe_arn
)
solution_arn = create_solution_response['solutionArn']
print(json.dumps(create_solution_response, indent=2))
create_solution_version_response = personalize.create_solution_version(
    solutionArn=solution_arn
)

solution_version_arn = create_solution_version_response['solutionVersionArn']
print(json.dumps(create_solution_version_response, indent=2))

solution_arn = create_solution_response['solutionArn']
print(json.dumps(create_solution_response, indent=2))
