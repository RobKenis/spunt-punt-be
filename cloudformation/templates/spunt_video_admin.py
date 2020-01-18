from troposphere import Template, constants, Parameter, ImportValue, Join, Ref, iam, GetAtt, awslambda, AWS_STACK_NAME
from troposphere.apigateway import BasePathMapping, DomainName, EndpointConfiguration
from troposphere.awslambda import Code, Environment, EventSourceMapping
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.dynamodb import Table, AttributeDefinition, KeySchema
from troposphere.iam import Role
from troposphere.logs import LogGroup
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget
from troposphere.serverless import Api, Function

template = Template(Description='Admin dashboard for spunt.be videos')
template.set_transform('AWS::Serverless-2016-10-31')

core_stack = template.add_parameter(Parameter(
    'CoreStack',
    Type=constants.STRING,
    Default='spunt-core',
))

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

domain_name = template.add_parameter(Parameter(
    'DomainName',
    Type=constants.STRING,
    Default='admin.spunt.be',
))

consume_events_code_key = template.add_parameter(Parameter(
    'ConsumeEvents',
    Type=constants.STRING,
    Default='lambda-code/admin/consume_admin_events.zip',
))

template.add_parameter_to_group(consume_events_code_key, 'Lambda Keys')

video_table = template.add_resource(Table(
    'VideoTable',
    BillingMode='PAY_PER_REQUEST',
    AttributeDefinitions=[AttributeDefinition(
        AttributeName='videoId',
        AttributeType='S',
    )],
    KeySchema=[KeySchema(
        AttributeName='videoId',
        KeyType='HASH',
    )],
))

consume_events_role = template.add_resource(Role(
    'ConsumeEventsRole',
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
        ImportValue(Join('-', [Ref(core_stack), 'EventsToDashboardQueuePolicy', 'Arn']))
    ],
    Policies=[iam.Policy(
        PolicyName="api-consume-events",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["dynamodb:UpdateItem"],
                "Resource": [GetAtt(video_table, 'Arn')],
                "Effect": "Allow",
            }],
        })],
))

consume_events_function = template.add_resource(awslambda.Function(
    'ConsumeEventsFunction',
    Description='Consumes events to build the admin video model.',
    Runtime='python3.7',
    Handler='index.handler',
    Role=GetAtt(consume_events_role, 'Arn'),
    Code=Code(
        S3Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        S3Key=Ref(consume_events_code_key),
    ),
    Environment=Environment(
        Variables={
            'VIDEO_TABLE': Ref(video_table),
        }
    ),
))

template.add_resource(LogGroup(
    "ConsumeEventsLogGroup",
    LogGroupName=Join('/', ['/aws/lambda', Ref(consume_events_function)]),
    RetentionInDays=7,
))

template.add_resource(EventSourceMapping(
    'InvokeConsumeEvents',
    EventSourceArn=ImportValue(Join('-', [Ref(core_stack), 'EventsToDashboardQueue-Arn'])),
    FunctionName=Ref(consume_events_function),
    Enabled=True,
))

admin_api = template.add_resource(Api(
    'AdminApi',
    StageName='v1',
    EndpointConfiguration='REGIONAL',
    # Cors=Cors(
    #     AllowHeaders='*',
    #     AllowMethods='*',
    #     AllowOrigin='*',
    # ),
))

all_videos_function = template.add_resource(Function(
    'AllVideosFunction',
    Handler='index.handler',
    Runtime='python3.7',
    Description='Returns list of videos for the admin api.',
    InlineCode="def handler(event, context):\n    return {'body': 'Hello World!','statusCode': 200}\n",
    Events={
        'ApiEvent': {
            'Properties': {
                'Method': 'get',
                'Path': '/videos',
                'RestApiId': Ref(admin_api),
            },
            'Type': 'Api',
        }
    }
))
api_certificate = template.add_resource(Certificate(
    "ApiCertificate",
    DomainName=Ref(domain_name),
    DomainValidationOptions=[DomainValidationOption(
        DomainName=Ref(domain_name),
        ValidationDomain=ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneName'])),
    )],
    ValidationMethod='DNS',
))

api_domain_name = template.add_resource(DomainName(
    'ApiDomainName',
    RegionalCertificateArn=Ref(api_certificate),
    DomainName=Ref(domain_name),
    EndpointConfiguration=EndpointConfiguration(
        Types=['REGIONAL'],
    ),
))

template.add_resource(BasePathMapping(
    'ApiMapping',
    DomainName=Ref(domain_name),
    RestApiId=Ref(admin_api),
    Stage='v1'
))

template.add_resource(RecordSetGroup(
    "DnsRecords",
    HostedZoneId=ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneId'])),
    RecordSets=[RecordSet(
        Name=Ref(domain_name),
        Type='A',
        AliasTarget=AliasTarget(
            HostedZoneId=GetAtt(api_domain_name, 'RegionalHostedZoneId'),
            DNSName=GetAtt(api_domain_name, 'RegionalDomainName'),
        ),
    ), RecordSet(
        Name=Ref(domain_name),
        Type='AAAA',
        AliasTarget=AliasTarget(
            HostedZoneId=GetAtt(api_domain_name, 'RegionalHostedZoneId'),
            DNSName=GetAtt(api_domain_name, 'RegionalDomainName'),
        ),
    )],
    Comment=Join('', ['Record for Api Gateway in ', Ref(AWS_STACK_NAME)]),
))

f = open("output/spunt_video_admin.json", "w")
f.write(template.to_json())
