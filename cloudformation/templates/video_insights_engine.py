from troposphere import Template, GetAtt, ImportValue, Join, Ref, constants, Parameter
from troposphere.awslambda import Function, Code, Environment, TracingConfig, EventSourceMapping
from troposphere.iam import Role
from troposphere.logs import LogGroup

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

template.add_parameter_to_group(start_insights_code_key, 'Lambda Keys')

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
        ImportValue(Join('-', [Ref(encoding_stack), 'LambdaDefaultPolicy-Arn'])),
        ImportValue(Join('-', [Ref(encoding_stack), 'ConsumeMediaInsightsQueuePolicy-Arn']))
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
            'VIDEO_EVENTS_TABLE': ImportValue(Join('-', [Ref(encoding_stack), 'VideoEventsTable-Ref'])),
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
