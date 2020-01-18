from troposphere import Template, Parameter, constants, Output, Ref, Export, Join, AWS_STACK_NAME, ImportValue, \
    AWS_REGION, GetAtt, AWSHelperFn, iam
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.cloudfront import Distribution, DistributionConfig, DefaultCacheBehavior, ForwardedValues, Origin, \
    CustomOriginConfig, ViewerCertificate, CacheBehavior, LambdaFunctionAssociation
from troposphere.iam import Role
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget
from troposphere.s3 import Bucket, WebsiteConfiguration
from troposphere.serverless import S3Location, Function


class VersionRef(AWSHelperFn):
    def __init__(self, data):
        func = self.getdata(data)
        self.data = {'Ref': "{function}.Version".format(function=func)}


template = Template('S3 and CloudFront for spunt.be')
template.set_transform('AWS::Serverless-2016-10-31')

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

core_stack = template.add_parameter(Parameter(
    'CoreStack',
    Type=constants.STRING,
    Default='spunt-core',
))

domain_name = template.add_parameter(Parameter(
    'DomainName',
    Type=constants.STRING,
    Default='spunt.be',
))

rewrite_assets_lambda_code_key = template.add_parameter(Parameter(
    'RewriteAssets',
    Type=constants.STRING,
    Default='lambda-code/frontend/rewrite_assets.zip',
))

template.add_parameter_to_group(rewrite_assets_lambda_code_key, 'Lambda Keys')

frontend_bucket = template.add_resource(Bucket(
    "FrontendBucket",
    AccessControl='PublicRead',  # Maybe remove this later on
    WebsiteConfiguration=WebsiteConfiguration(
        IndexDocument='index.html',
        ErrorDocument='index.html',
    ),
))

cloudfront_certificate = template.add_resource(Certificate(
    "CloudFrontCertificate",
    DomainName=Ref(domain_name),
    DomainValidationOptions=[DomainValidationOption(
        DomainName=Ref(domain_name),
        ValidationDomain=ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneName'])),
    )],
    ValidationMethod='DNS',
))

readonly_function_role = template.add_resource(Role(
    'ReadonlyLambdaRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]},
        }],
    },
    Policies=[iam.Policy(
        PolicyName="spunt-be-readonly",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ['logs:CreateLogGroup', "logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": "arn:aws:logs:*:*:*",
                "Effect": "Allow",
            }],
        })],
))

rewrite_assets_function = template.add_resource(Function(
    'RewriteAssetsFunction',
    Description='Rewrite assets based on CloudFront headers.',
    Runtime='nodejs10.x',
    Handler='index.handler',
    Role=GetAtt(readonly_function_role, 'Arn'),
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(rewrite_assets_lambda_code_key),
    ),
))

public_distribution = template.add_resource(Distribution(
    "CloudFrontDistribution",
    DistributionConfig=DistributionConfig(
        Aliases=[Ref(domain_name)],
        Comment=Ref(AWS_STACK_NAME),
        DefaultCacheBehavior=DefaultCacheBehavior(
            TargetOriginId='S3',
            ViewerProtocolPolicy='redirect-to-https',
            ForwardedValues=ForwardedValues(
                QueryString=False,
            ),
            MinTTL=120,  # 2 minutes
            DefaultTTL=300,  # 5 minutes
            MaxTTL=300  # 5 minutes
        ),
        CacheBehaviors=[CacheBehavior(
            TargetOriginId="S3",
            PathPattern='/src.*.css',
            ViewerProtocolPolicy='redirect-to-https',
            AllowedMethods=['GET', 'HEAD', 'OPTIONS'],
            CachedMethods=['GET', 'HEAD', 'OPTIONS'],
            ForwardedValues=ForwardedValues(
                QueryString=False,
                Headers=['CloudFront-Is-Desktop-Viewer', 'CloudFront-Is-Mobile-Viewer', 'CloudFront-Is-Tablet-Viewer'],
            ),
            MinTTL=120,  # 2 minutes
            DefaultTTL=300,  # 5 minutes
            MaxTTL=300,  # 5 minutes
            Compress=True,
            LambdaFunctionAssociations=[LambdaFunctionAssociation(
                EventType='origin-request',
                LambdaFunctionARN=VersionRef(rewrite_assets_function),
            )],
        )],
        Enabled=True,
        HttpVersion='http2',
        IPV6Enabled=True,
        Origins=[Origin(
            DomainName=Join('', [Ref(frontend_bucket), '.s3-website-', Ref(AWS_REGION), '.amazonaws.com']),
            Id='S3',
            CustomOriginConfig=CustomOriginConfig(
                OriginProtocolPolicy='http-only',
            ),
        )],
        PriceClass='PriceClass_100',
        ViewerCertificate=ViewerCertificate(
            AcmCertificateArn=Ref(cloudfront_certificate),
            SslSupportMethod='sni-only',
            MinimumProtocolVersion='TLSv1.1_2016',  # We might need to raise this
        ),
    ),
))

template.add_resource(RecordSetGroup(
    "DnsRecords",
    HostedZoneId=ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneId'])),
    RecordSets=[RecordSet(
        Name=Ref(domain_name),
        Type='A',
        AliasTarget=AliasTarget(
            HostedZoneId='Z2FDTNDATAQYW2',
            DNSName=GetAtt(public_distribution, 'DomainName'),
        ),
    ), RecordSet(
        Name=Ref(domain_name),
        Type='AAAA',
        AliasTarget=AliasTarget(
            HostedZoneId='Z2FDTNDATAQYW2',
            DNSName=GetAtt(public_distribution, 'DomainName'),
        ),
    )],
    Comment=Join('', ['Record for CloudFront in ', Ref(AWS_STACK_NAME)]),
))

template.add_output(Output(
    'FrontendBucket',
    Description='Name of the frontend bucket',
    Value=Ref(frontend_bucket),
    Export=Export(Join('-', [Ref(AWS_STACK_NAME), 'FrontendBucket', 'Ref']))
))

f = open("output/spunt_be.json", "w")
f.write(template.to_json())
