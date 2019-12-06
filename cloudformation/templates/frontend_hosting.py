from troposphere import Template, Parameter, constants, Output, Ref, Export, Join, AWS_STACK_NAME, ImportValue, \
    AWS_REGION, GetAtt
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.cloudfront import Distribution, DistributionConfig, DefaultCacheBehavior, ForwardedValues, Origin, \
    CustomOriginConfig, ViewerCertificate
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget
from troposphere.s3 import Bucket, WebsiteConfiguration

template = Template('S3 and CloudFront for spunt.be')

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

domain_name = template.add_parameter(Parameter(
    'DomainName',
    Type=constants.STRING,
    Default='spunt.be',
))

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

f = open("output/frontend_hosting.json", "w")
f.write(template.to_json())
