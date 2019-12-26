from troposphere import Template, Ref, Join, AWS_STACK_NAME, GetAtt, constants, Parameter, ImportValue, iam, \
    AWSProperty, awslambda, ssm, AWS_REGION, AWS_ACCOUNT_ID
from troposphere.awslambda import Function, Environment, Code, EventInvokeConfig, OnFailure, \
    TracingConfig, Permission
from troposphere.cloudformation import AWSCustomObject
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema
from troposphere.iam import Role, Policy, ManagedPolicy
from troposphere.logs import LogGroup
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations, Filter, S3Key, Rules, \
    CorsConfiguration, CorsRules
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
_pipeline_id_parameter = Join('.', [Ref(AWS_STACK_NAME), 'elastictranscoder', 'id'])

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

request_encoding_lambda_code_key = template.add_parameter(Parameter(
    'RequestEncoding',
    Type=constants.STRING,
    Default='lambda-code/video_engine/request_encoding.zip',
))

elastictranscoder_code_key = template.add_parameter(Parameter(
    'ElasticTranscoder',
    Type=constants.STRING,
    Default='custom_resources/elastictranscoder.zip',
))

template.add_parameter_to_group(start_encode_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(request_encoding_lambda_code_key, 'Lambda Keys')
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
            "Resource": [Join('', [
                'arn:aws:ssm:',
                Ref(AWS_REGION),
                ':',
                Ref(AWS_ACCOUNT_ID),
                ':parameter/',
                Ref(AWS_STACK_NAME),
                '*'
            ])],
            "Effect": "Allow",
        }],
    }
))

request_encoding_lambda_role = template.add_resource(Role(
    'RequestEncodingLambdaRole',
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
        PolicyName="request-encoding",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["sqs:SendMessage"],
                "Resource": [GetAtt(processing_failed_queue, 'Arn')],
                "Effect": "Allow",
            }, {
                "Action": ["elastictranscoder:CreateJob"],
                "Resource": ['*'],
                "Effect": "Allow",
            }],
        })],
))

request_encoding_function = template.add_resource(Function(
    'RequestEncodingFunction',
    Description='Creates Elastic Transcoder job web formats.',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(request_encoding_lambda_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(request_encoding_lambda_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_EVENTS_TABLE': Ref(video_events_table),
            'PIPELINE_ID_PARAMETER': _pipeline_id_parameter,
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
))

template.add_resource(LogGroup(
    "RequestEncodingLambdaLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(request_encoding_function)]),
    RetentionInDays=7,
))

request_encoding_topic = template.add_resource(Topic(
    'RequestEncodingTopic',
    Subscription=[Subscription(
        Protocol='sqs',
        Endpoint=GetAtt(request_encoding_queue, 'Arn'),
    ), Subscription(
        Protocol='lambda',
        Endpoint=GetAtt(request_encoding_function, 'Arn'),
    )],
))

template.add_resource(Permission(
    'InvokeRequestEncodingFunctionPermission',
    Action='lambda:InvokeFunction',
    FunctionName=Ref(request_encoding_function),
    Principal='sns.amazonaws.com',
    SourceArn=Ref(request_encoding_topic),
))

template.add_resource(EventInvokeConfig(
    'RequestEncodingInvokeConfig',
    FunctionName=Ref(request_encoding_function),
    MaximumEventAgeInSeconds=60,
    MaximumRetryAttempts=1,
    Qualifier='$LATEST',
    DestinationConfig=DestinationConfig(
        OnFailure=OnFailure(
            Destination=GetAtt(processing_failed_queue, 'Arn'),
        ),
    ),
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
    ManagedPolicyArns=[Ref(lambda_managed_policy)],
    Policies=[iam.Policy(
        PolicyName="start-encode",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["sqs:SendMessage"],
                "Resource": [GetAtt(processing_failed_queue, 'Arn'), GetAtt(request_encoding_queue, 'Arn')],
                "Effect": "Allow",
            }, {
                "Action": ["sns:Publish"],
                "Resource": [Ref(request_encoding_topic)],
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
    CorsConfiguration=CorsConfiguration(
        CorsRules=[CorsRules(
            AllowedOrigins=['*'],
            AllowedMethods=['GET', 'HEAD'],
            AllowedHeaders=['*'],
        )]
    ),
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

template.add_resource(TopicPolicy(
    'RequestEncodeTopicPolicy',
    Topics=[Ref(request_encoding_topic)],
    PolicyDocument={
        "Version": "2008-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": ["SNS:Publish"],
                "Resource": Ref(request_encoding_topic),
                "Condition": {"ArnLike": {"aws:SourceArn": GetAtt(start_encode_function, 'Arn')}},
            },
        ],
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
            Destination=Ref(request_encoding_topic),
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
    Description='Creates the Elastic Transcoder Pipeline custom resource.',
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

transcoder_role = template.add_resource(Role(
    "ElasticTranscoderPipelineRole",
    Policies=[Policy(
        PolicyName="ElasticTranscoderExecutionPolicy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }, {
                "Effect": "Allow",
                "Action": [
                    "elastictranscoder:*",
                    "iam:PassRole"
                ],
                "Resource": ["*"]
            }, {"Effect": "Allow",
                "Action": [
                    "s3:Get*"
                ],
                "Resource": [GetAtt(upload_bucket, 'Arn'), Join('', [GetAtt(upload_bucket, 'Arn'), '/*'])]
                }, {
                "Effect": "Allow",
                "Action": [
                    "s3:*"
                ],
                "Resource": [GetAtt(video_bucket, 'Arn'), Join('', [GetAtt(video_bucket, 'Arn'), '/*'])]
            }, {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": [Ref(encoding_updates_topic)]
            }]
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

transcoder_pipeline = template.add_resource(Pipeline(
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

template.add_resource(ssm.Parameter(
    'ElasticTranscoderPipelineParameter',
    Type='String',
    Value=Ref(transcoder_pipeline),
    Name=_pipeline_id_parameter,
    Description='ID of the Elastic Transcoder Pipeline used for encoding.'
))

f = open("output/video_engine.json", "w")
f.write(template.to_json())
