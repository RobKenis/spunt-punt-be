from troposphere import Template, GetAtt, ImportValue, Join, Ref, constants, Parameter, Sub
from troposphere.awslambda import Function, Code, Environment, TracingConfig, EventSourceMapping
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup
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
        }
    ),
    TracingConfig=TracingConfig(
        Mode='Active',
    ),
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

f = open("output/video_insights_engine.json", "w")
f.write(template.to_json())
