import os

import boto3
from invoke import task

CLOUDFORMATION_TEMPLATES_DIR = 'templates'

client = boto3.client('cloudformation')


@task
def build(c, docs=False):
    for filename in os.listdir(CLOUDFORMATION_TEMPLATES_DIR):
        print("Building {file}".format(file=filename))
        os.system("python {base}/{file}".
                  format(base=CLOUDFORMATION_TEMPLATES_DIR, file=filename))
        print("\t-> Finished building {file}".format(file=filename))


@task
def deploy(c, docs=False):
    with open('output/spunt_be.json', 'r') as template_body:
        client.update_stack(
            StackName='spunt-punt-be',
            TemplateBody=template_body.read(),
            Capabilities=['CAPABILITY_IAM'],
        )
