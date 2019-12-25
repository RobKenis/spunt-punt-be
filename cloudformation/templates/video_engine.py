from troposphere import Template, Ref, Join, AWS_STACK_NAME, GetAtt, constants, Parameter, ImportValue, iam, \
    AWSProperty, awslambda
from troposphere.awslambda import Function, Environment, Code, EventInvokeConfig, OnFailure, \
    TracingConfig, Permission
from troposphere.cloudformation import AWSCustomObject
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations, Filter, S3Key, Rules
from troposphere.sns import Topic, TopicPolicy, Subscription
from troposphere.sqs import Queue, QueuePolicy


class OnSuccess(AWSProperty):
    props = {
        'Destination': (str, True),
    }


class DestinationConfig(awslambda.DestinationConfig):
    props = {
        'OnSuccess': (OnSuccess, False),
        'OnFailure': (OnFailure, True),
    }


class Pipeline(AWSCustomObject):
    resource_type = "Custom::ElasticTranscoderPipeline"

    props = {
        'ServiceToken': (str, True),
        'Name': (str, True),
        'Role': (str, True),
        'InputBucket': (str, True),
        'OutputBucket': (str, False),
        'AwsKmsKeyArn': (str, False),
        'ContentConfig': (object, False),
        'ThumbnailConfig': (object, False),
        'Notifications': (object, False),
    }


template = Template(Description='Video engine for spunt.be')

_upload_bucket_name = Join('-', [Ref(AWS_STACK_NAME), 'upload'])

core_stack = template.add_parameter(Parameter(
    'CoreStack',
    Type=constants.STRING,
    Default='spunt-core',
))

start_encode_lambda_code_key = template.add_parameter(Parameter(
    'StartEncode',
    Type=constants.STRING,
    Default='lambda-code/video_engine/start_encode.zip',
))

elastictranscoder_code_key = template.add_parameter(Parameter(
    'ElasticTranscoder',
    Type=constants.STRING,
    Default='custom_resources/elastictranscoder.zip',
))

template.add_parameter_to_group(start_encode_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(elastictranscoder_code_key, 'Lambda Keys')

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

request_encoding_queue = template.add_resource(Queue(
    'RequestEncodingQueue',
))

processing_failed_queue = template.add_resource(Queue(
    'ProcessingFailedQueue',
))

start_encode_lambda_role = template.add_resource(Role(
    'StartEncodeLambdaRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    Policies=[iam.Policy(
        PolicyName="start-encode",
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
                "Action": ["sqs:SendMessage"],
                "Resource": [GetAtt(processing_failed_queue, 'Arn'), GetAtt(request_encoding_queue, 'Arn')],
                "Effect": "Allow",
            }],
        })],
))

start_encode_function = template.add_resource(Function(
    'StartEncodeFunction',
    Description='Consumes new video events and starts the encode.',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(start_encode_lambda_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(start_encode_lambda_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_EVENTS_TABLE': Ref(video_events_table),
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
))

template.add_resource(LogGroup(
    "StartEncodeLambdaLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(start_encode_function)]),
    RetentionInDays=7,
))

upload_topic = template.add_resource(Topic(
    'UploadTopic',
    Subscription=[Subscription(
        Endpoint=GetAtt(start_encode_function, 'Arn'),
        Protocol='lambda',
    )],
))

template.add_resource(TopicPolicy(
    'UploadTopicPolicy',
    Topics=[Ref(upload_topic)],
    PolicyDocument={
        "Version": "2008-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "s3.amazonaws.com"},
                "Action": ["SNS:Publish"],
                "Resource": Ref(upload_topic),
                "Condition": {"ArnLike": {"aws:SourceArn": Join("", ["arn:aws:s3:::", _upload_bucket_name])}},
            },
        ],
    },
))

template.add_resource(Permission(
    'InvokeStartEncodeFunctionPermission',
    Action='lambda:InvokeFunction',
    FunctionName=Ref(start_encode_function),
    Principal='sns.amazonaws.com',
    SourceArn=Ref(upload_topic),
))

upload_bucket = template.add_resource(Bucket(
    'UploadBucket',
    BucketName=_upload_bucket_name,  # Setting the bucket name is stupid, but this resolves a circular dependency.
    NotificationConfiguration=NotificationConfiguration(
        TopicConfigurations=[TopicConfigurations(
            Event='s3:ObjectCreated:*',
            Filter=Filter(
                S3Key=S3Key(
                    Rules=[Rules(
                        Name='prefix',
                        Value='upload/',
                    )],
                ),
            ),
            Topic=Ref(upload_topic)
        )],
    ),
))

video_bucket = template.add_resource(Bucket(
    'VideoBucket',
))

template.add_resource(QueuePolicy(
    "StartEncodingDestinationQueuesPolicy",
    Queues=[Ref(request_encoding_queue), Ref(processing_failed_queue)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(request_encoding_queue, 'Arn'),
            "Principal": '*',  # This could be a little stricter
        }, {
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(processing_failed_queue, 'Arn'),
            "Principal": '*',  # This could be a little stricter
        }],
    },
))

template.add_resource(EventInvokeConfig(
    'StartEncodeInvokeConfig',
    FunctionName=Ref(start_encode_function),
    MaximumEventAgeInSeconds=60,
    MaximumRetryAttempts=1,
    Qualifier='$LATEST',
    DestinationConfig=DestinationConfig(
        OnSuccess=OnSuccess(
            Destination=GetAtt(request_encoding_queue, 'Arn'),
        ),
        OnFailure=OnFailure(
            Destination=GetAtt(processing_failed_queue, 'Arn'),
        ),
    ),
))

elastictranscoder_custom_resource_role = template.add_resource(Role(
    'ElasticTranscoderCustomResourceRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    Policies=[Policy(
        PolicyName="start-encode",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": "arn:aws:logs:*:*:*",
                "Effect": "Allow",
            }, {
                "Effect": "Allow",
                "Action": [
                    "elastictranscoder:CreatePipeline",
                    "elastictranscoder:DeletePipeline",
                    "elastictranscoder:ReadPipeline",
                    "elastictranscoder:UpdatePipeline"
                ],
                "Resource": "*"
            }, {
                "Action": ["iam:PassRole"],
                "Effect": "Allow",
                "Resource": "*"
            }],
        })],
))

elastictranscoder_custom_resource_function = template.add_resource(Function(
    "ElasticTranscoderCustomResourceFunction",
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(elastictranscoder_code_key),
    ),
    Handler='index.handler',
    Role=GetAtt(elastictranscoder_custom_resource_role, "Arn"),
    Runtime='nodejs10.x',
))

template.add_resource(LogGroup(
    "ElasticTranscoderCustomResourceLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(elastictranscoder_custom_resource_function)]),
    RetentionInDays=7,
))

transcoder_role = template.add_resource(Role(
    "ElasticTranscoderPipelineRole",
    Policies=[Policy(
        PolicyName="ElasticTranscoderExecutionPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elastictranscoder:*",
                        "iam:PassRole"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:Get*"
                    ],
                    "Resource": [
                        GetAtt(upload_bucket, 'Arn'),
                        Join('', [GetAtt(upload_bucket, 'Arn'), '/*']),
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:*"
                    ],
                    "Resource": [
                        GetAtt(video_bucket, 'Arn'),
                        Join('', [GetAtt(video_bucket, 'Arn'), '/*']),
                    ]
                }
            ]
        },
    )],
    AssumeRolePolicyDocument={"Version": "2012-10-17", "Statement": [
        {
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "lambda.amazonaws.com",
                    "elastictranscoder.amazonaws.com"
                ]
            }
        }
    ]},
))

encoding_updates_queue = template.add_resource(Queue(
    'EncodingUpdatesQueue',
))

encoding_updates_topic = template.add_resource(Topic(
    'EncodingUpdatesTopic',
    Subscription=[Subscription(
        Endpoint=GetAtt(encoding_updates_queue, 'Arn'),
        Protocol='sqs',
    )],
))

template.add_resource(QueuePolicy(
    "EncodingUpdatesQueuePolicy",
    Queues=[Ref(encoding_updates_queue)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(encoding_updates_queue, 'Arn'),
            "Principal": {"Service": "sns.amazonaws.com"},
            "Condition": {"ArnEquals": {"aws:SourceArn": Ref(encoding_updates_topic)}},
        }],
    },
))

template.add_resource(Pipeline(
    "ElasticTranscoderPipeline",
    ServiceToken=GetAtt(elastictranscoder_custom_resource_function, 'Arn'),
    Name=Ref(AWS_STACK_NAME),
    Role=GetAtt(transcoder_role, "Arn"),
    InputBucket=Ref(upload_bucket),
    OutputBucket=Ref(video_bucket),
    Notifications={
        'Completed': Ref(encoding_updates_topic),
        'Error': Ref(encoding_updates_topic),
        'Progressing': Ref(encoding_updates_topic),
        'Warning': Ref(encoding_updates_topic),
    },
))

f = open("output/video_engine.json", "w")
f.write(template.to_json())
