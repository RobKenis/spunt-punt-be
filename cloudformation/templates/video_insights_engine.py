from troposphere import Template, GetAtt, ImportValue, Join, Ref, constants, Parameter, Sub, AWS_STACK_NAME
from troposphere.awslambda import Function, Code, Environment, TracingConfig, EventSourceMapping
from troposphere.events import EventBus, Rule, Target
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup
from troposphere.sns import Topic, Subscription
from troposphere.sqs import Queue, QueuePolicy
from troposphere.stepfunctions import StateMachine

template = Template(Description='Video insights engine for spunt.be')

core_stack = template.add_parameter(Parameter(
    'CoreStack',
    Type=constants.STRING,
    Default='spunt-core',
))

encoding_stack = template.add_parameter(Parameter(
    'VideoEncodingStack',
    Type=constants.STRING,
    Default='spunt-video-encoding-engine',
))

start_insights_code_key = template.add_parameter(Parameter(
    'StartInsights',
    Type=constants.STRING,
    Default='lambda-code/video_engine/start_insights.zip',
))

rekognition_code_key = template.add_parameter(Parameter(
    'Rekognition',
    Type=constants.STRING,
    Default='lambda-code/video_engine/rekognition.zip',
))

video_metadata_event_code_key = template.add_parameter(Parameter(
    'VideoMetadataEvent',
    Type=constants.STRING,
    Default='lambda-code/video_engine/video_metadata_event.zip',
))

template.add_parameter_to_group(start_insights_code_key, 'Lambda Keys')
template.add_parameter_to_group(rekognition_code_key, 'Lambda Keys')
template.add_parameter_to_group(video_metadata_event_code_key, 'Lambda Keys')

rekognition_updates_queue = template.add_resource(Queue(
    'RekognitionUpdatesQueue',
))

rekognition_updates_topic = template.add_resource(Topic(
    'RekognitionUpdatesTopic',
    Subscription=[Subscription(
        Endpoint=GetAtt(rekognition_updates_queue, 'Arn'),
        Protocol='sqs',
    )],
))

template.add_resource(QueuePolicy(
    "RekognitionUpdatesQueuePolicy",
    Queues=[Ref(rekognition_updates_queue)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(rekognition_updates_queue, 'Arn'),
            "Principal": {"Service": "sns.amazonaws.com"},
            "Condition": {"ArnEquals": {"aws:SourceArn": Ref(rekognition_updates_topic)}},
        }],
    },
))

rekognition_publish_role = template.add_resource(Role(
    'RekognitionPublishRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["rekognition.amazonaws.com"]},
        }],
    },
    Policies=[Policy(
        PolicyName="put-rekognition-status-on-topic",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sns:Publish"
                    ],
                    "Resource": Ref(rekognition_updates_topic),
                },
            ]
        })],
))

rekognition_role = template.add_resource(Role(
    'RekognitionRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    ManagedPolicyArns=[
        ImportValue(Join('-', [Ref(core_stack), 'LambdaDefaultPolicy', 'Arn'])),
    ],
    Policies=[Policy(
        PolicyName="rekognition",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["rekognition:StartLabelDetection"],
                    "Resource": '*',
                },
                {
                    "Effect": "Allow",
                    "Action": ["iam:PassRole"],
                    "Resource": GetAtt(rekognition_publish_role, 'Arn'),
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:Get*"],
                    "Resource": Join('', [
                        'arn:aws:s3:::',
                        ImportValue(Join('-', [Ref(encoding_stack), 'UploadBucket', 'Ref'])),
                        '/*',
                    ]),
                },
            ]
        })],
))

rekognition_function = template.add_resource(Function(
    'RekognitionFunction',
    Description='Extracts video metadata using Rekognition',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(rekognition_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(rekognition_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_EVENTS_TABLE': ImportValue(Join('-', [Ref(core_stack), 'VideoEventsTable', 'Ref'])),
            'REKOGNITION_UPDATES_TOPIC': Ref(rekognition_updates_topic),
            'REKOGNITION_ROLE_ARN': GetAtt(rekognition_publish_role, 'Arn'),
            'INPUT_BUCKET': ImportValue(Join('-', [Ref(encoding_stack), 'UploadBucket', 'Ref'])),
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
))

template.add_resource(LogGroup(
    "RekognitionFunctionLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(rekognition_function)]),
    RetentionInDays=7,
))

video_metadata_event_role = template.add_resource(Role(
    'VideoMetadataEventRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    ManagedPolicyArns=[
        ImportValue(Join('-', [Ref(core_stack), 'LambdaDefaultPolicy', 'Arn'])),
    ],
))

video_metadata_event_function = template.add_resource(Function(
    'VideoMetadataEventFunction',
    Description='Transforms video Rekognition metadata to an event.',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(video_metadata_event_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(video_metadata_event_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_EVENTS_TABLE': ImportValue(Join('-', [Ref(core_stack), 'VideoEventsTable', 'Ref'])),
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
))

step_function_role = template.add_resource(Role(
    'StepFunctionRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["states.amazonaws.com"]},
        }],
    },
    Policies=[Policy(
        PolicyName="invoke-lambda",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["lambda:InvokeFunction"],
                "Effect": "Allow",
                "Resource": [
                    GetAtt(rekognition_function, 'Arn'),
                    GetAtt(video_metadata_event_function, 'Arn'),
                ],
            }],
        })],
))

with open('resources/state_machine_definitions/video_metadata.json', 'r') as definition:
    video_step_function = template.add_resource(StateMachine(
        'VideoStepFunction',
        DefinitionString=Sub(definition.read()),
        RoleArn=GetAtt(step_function_role, 'Arn'),
    ))

event_bus = template.add_resource(EventBus(
    'InsightsEventBus',
    Name=Ref(AWS_STACK_NAME),
))

event_bridge_role = template.add_resource(Role(
    'EventBridgeRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["events.amazonaws.com"]},
        }],
    },
    Policies=[Policy(
        PolicyName="invoke-step-function",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["states:StartExecution"],
                "Effect": "Allow",
                "Resource": [
                    Ref(video_step_function),
                ],
            }],
        })],
))

template.add_resource(Rule(
    'StartMetadataRule',
    Description='Routes start metadata events to the corresponding step functions',
    EventBusName=Ref(event_bus),
    EventPattern={"source": ["spunt.video.events"]},
    Targets=[
        Target(
            Arn=Ref(video_step_function),
            Id='VideoStepFunction',
            RoleArn=GetAtt(event_bridge_role, 'Arn'),
        )
    ]
))

start_insights_role = template.add_resource(Role(
    'StartInsightsLambdaRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com"]},
        }],
    },
    ManagedPolicyArns=[
        ImportValue(Join('-', [Ref(core_stack), 'LambdaDefaultPolicy', 'Arn'])),
        ImportValue(Join('-', [Ref(encoding_stack), 'ConsumeMediaInsightsQueuePolicy', 'Arn']))
    ],
    Policies=[Policy(
        PolicyName="put-events",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["events:PutEvents"],
                "Effect": "Allow",
                "Resource": [GetAtt(event_bus, 'Arn')],
            }],
        })],
))

start_insights_function = template.add_resource(Function(
    'StartInsightsFunction',
    Description='Consumes messages to start media insights for video.',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(start_insights_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(start_insights_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_EVENTS_TABLE': ImportValue(Join('-', [Ref(core_stack), 'VideoEventsTable', 'Ref'])),
            'EVENT_BUS_NAME': Ref(event_bus),
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
))

template.add_resource(LogGroup(
    "StartInsightsLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(start_insights_function)]),
    RetentionInDays=7,
))

template.add_resource(EventSourceMapping(
    'InvokeStartInsights',
    EventSourceArn=ImportValue(Join('-', [Ref(encoding_stack), 'StartMediaInsightsQueue-Arn'])),
    FunctionName=Ref(start_insights_function),
    Enabled=True,
))

f = open("output/video_insights_engine.json", "w")
f.write(template.to_json())
