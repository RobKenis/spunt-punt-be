from troposphere import Template, Output, Ref, Export, Join, AWS_STACK_NAME, GetAtt
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema
from troposphere.iam import ManagedPolicy
from troposphere.s3 import Bucket

template = Template(Description='Core resources for spunt.be')

lambda_code_bucket = template.add_resource(Bucket(
    'LambdaCodeBucket',
))

# Events table
video_events_table = template.add_resource(Table(
    'VideoEventsTable',
    BillingMode='PAY_PER_REQUEST',
    AttributeDefinitions=[AttributeDefinition(
        AttributeName='videoId',
        AttributeType='S',
    ), AttributeDefinition(
        AttributeName='timestamp',
        AttributeType='S',
    )],
    KeySchema=[KeySchema(
        AttributeName='videoId',
        KeyType='HASH',
    ), KeySchema(
        AttributeName='timestamp',
        KeyType='RANGE',
    )],
))

# Managed policies
lambda_managed_policy = template.add_resource(ManagedPolicy(
    'LambdaDefaultPolicy',
    Description='Allows default actions for video-engine lambdas',
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
            "Resource": "arn:aws:logs:*:*:*",
            "Effect": "Allow",
        }, {
            "Action": ["xray:PutTraceSegments"],
            "Resource": "*",
            "Effect": "Allow",
        }, {
            "Action": ["dynamodb:PutItem"],
            "Resource": [GetAtt(video_events_table, 'Arn')],
            "Effect": "Allow",
        }, {
            "Action": ["ssm:GetParameter"],
            "Resource": ['*'],  # Find a way to restrict this
            "Effect": "Allow",
        }],
    }
))

template.add_output(Output(
    "LambdaCodeBucket",
    Description='Name of the bucket where all the lambda code is located.',
    Value=Ref(lambda_code_bucket),
    Export=Export(Join("-", [Ref(AWS_STACK_NAME), 'LambdaCodeBucket-Ref'])),
))

template.add_output(Output(
    "LambdaDefaultPolicy",
    Description='ARN of the managed policy that allows basic lambda actions.',
    Value=Ref(lambda_managed_policy),
    Export=Export(Join("-", [Ref(AWS_STACK_NAME), 'LambdaDefaultPolicy', 'Arn'])),
))

template.add_output(Output(
    "VideoEventsTable",
    Description='Name of the video-events table.',
    Value=Ref(video_events_table),
    Export=Export(Join("-", [Ref(AWS_STACK_NAME), 'VideoEventsTable', 'Ref'])),
))

f = open("output/core.json", "w")
f.write(template.to_json())
