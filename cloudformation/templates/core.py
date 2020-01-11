from troposphere import Template, Output, Ref, Export, Join, AWS_STACK_NAME, GetAtt, iam
from troposphere.awslambda import Environment
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema, StreamSpecification
from troposphere.iam import ManagedPolicy, Role
from troposphere.logs import LogGroup
from troposphere.s3 import Bucket
from troposphere.serverless import Function
from troposphere.sqs import Queue

template = Template(Description='Core resources for spunt.be')
template.set_transform('AWS::Serverless-2016-10-31')

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
    StreamSpecification=StreamSpecification(
        StreamViewType='NEW_IMAGE',
    ),
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

events_to_api_queue = template.add_resource(Queue(
    'EventsToApiQueue',
))

event_to_dashboard_queue = template.add_resource(Queue(
    'EventsToDashboardQueue',
))

event_router_role = template.add_resource(Role(
    'EventRouterRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    ManagedPolicyArns=[Ref(lambda_managed_policy)],
    Policies=[iam.Policy(
        PolicyName="video-event-router",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["dynamodb:DescribeStream", "dynamodb:GetRecords",
                           "dynamodb:GetShardIterator", "dynamodb:ListStreams"],
                "Resource": [Join('', [GetAtt(video_events_table, 'Arn'), '/stream/*'])],
                "Effect": "Allow",
            }, {
                "Action": ["sqs:SendMessage"],
                "Resource": [GetAtt(events_to_api_queue, 'Arn'), GetAtt(event_to_dashboard_queue, 'Arn')],
                "Effect": "Allow",
            }],
        })],
))

with open('resources/spunt_core/event_router/index.py', 'r') as lambda_code:
    event_router_function = template.add_resource(Function(
        'EventRouterFunction',
        Handler='index.handler',
        Runtime='python3.7',
        InlineCode=lambda_code.read(),
        Description='Consumes events dynamoDB stream and routes events to corresponding queues.',
        Role=GetAtt(event_router_role, 'Arn'),
        Environment=Environment(
            Variables={
                'API_EVENTS_QUEUE_URL': Ref(events_to_api_queue),
                'DASHBOARD_EVENTS_QUEUE_URL': Ref(event_to_dashboard_queue),
            },
        ),
        Events={
            'VideoEventsStream': {
                'Type': 'DynamoDB',
                'Properties': {
                    'Enabled': True,
                    'StartingPosition': 'TRIM_HORIZON',
                    'Stream': GetAtt(video_events_table, 'StreamArn'),
                }
            }
        },
    ))

template.add_resource(LogGroup(
    "EventRouterFunctionLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(event_router_function)]),
    RetentionInDays=7,
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
