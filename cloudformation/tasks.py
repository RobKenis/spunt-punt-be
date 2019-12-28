import os

import boto3
from invoke import task

CLOUDFORMATION_TEMPLATES_DIR = 'templates'

client = boto3.client('cloudformation')
s3 = boto3.client('s3')

STACKS = {
    'spunt-punt-be': 'output/spunt_be.json',
    'spunt-video-engine': 'output/video_engine.json',
    'spunt-core': 'output/core.json',
}


@task
def build(c, docs=False, code=False, templates=True):
    if templates:
        print('Building CloudFormation . . .')
        for filename in os.listdir(CLOUDFORMATION_TEMPLATES_DIR):
            print("Building {file}".format(file=filename))
            os.system("python {base}/{file}".
                      format(base=CLOUDFORMATION_TEMPLATES_DIR, file=filename))
            print("\t-> Finished building {file}".format(file=filename))
    if code:
        print('Building lambda code . . .')
        os.system("./build.sh")


@task
def deploy(c, stack, docs=False):
    with open(STACKS[stack], 'r') as template_body:
        client.update_stack(
            StackName=stack,
            TemplateBody=template_body.read(),
            Capabilities=['CAPABILITY_IAM'],
        )


@task  # This is invoked as 'upload-lambda', no idea why..
def upload_lambda(c, docs=False):
    response = client.describe_stacks(
        StackName='spunt-core',
    )
    # Some very fool-proof, indestructible python.
    bucket = next((item for item in response['Stacks'][0]['Outputs']
                   if item["OutputKey"] == "LambdaCodeBucket"), None)['OutputValue']
    print("Uploading lambda code to {bucket}".format(bucket=bucket))
    s3.put_object(
        Bucket=bucket,
        Body='output/start_encode.zip',
        Key='lambda-code/video_engine/start_encode.zip',
    )


@task
def clean(c, docs=False):
    os.system('rm output/*.json output/*.zip')
