from troposphere import Template, Ref, Join, AWS_STACK_NAME, GetAtt, constants, Parameter, ImportValue, iam
from troposphere.awslambda import Function, Environment, Code, EventSourceMapping
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations, Filter, S3Key, Rules
from troposphere.sns import Topic, TopicPolicy, Subscription
from troposphere.sqs import Queue, QueuePolicy

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
template.add_parameter_to_group(start_encode_lambda_code_key, 'Lambda Keys')

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

encode_video_queue = template.add_resource(Queue(
    'EncodeVideoQueue'
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
                "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                "Resource": GetAtt(encode_video_queue, 'Arn'),
                "Effect": "Allow",
            }, {
                "Action": ["dynamodb:PutItem"],
                "Resource": [GetAtt(video_events_table, 'Arn')],
                "Effect": "Allow",
            }],
        })],
))

start_encode_function = template.add_resource(Function(
    'StartEncodeFunction',
    Description='Consumes new video events and start the encode.',
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
))

template.add_resource(LogGroup(
    "StartEncodeLambdaLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(start_encode_function)]),
    RetentionInDays=7,
))

template.add_resource(EventSourceMapping(
    "StartEncodeOnNewMessage",
    BatchSize=1,
    Enabled=True,
    EventSourceArn=GetAtt(encode_video_queue, 'Arn'),
    FunctionName=Ref(start_encode_function),
))

upload_topic = template.add_resource(Topic(
    'UploadTopic',
    Subscription=[Subscription(
        Endpoint=GetAtt(encode_video_queue, 'Arn'),
        Protocol='SQS',
    )],
))

template.add_resource(QueuePolicy(
    "EncodeVideoQueuePolicy",
    Queues=[Ref(encode_video_queue)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(encode_video_queue, 'Arn'),
            "Principal": {"Service": "sns.amazonaws.com"},
            "Condition": {"ArnEquals": {"aws:SourceArn": Ref(upload_topic)}},
        }],
    },
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

f = open("output/video_engine.json", "w")
f.write(template.to_json())
