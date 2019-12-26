from troposphere import Template, Join, Ref, AWS_REGION, ImportValue, GetAtt, AWS_STACK_NAME, Parameter, constants
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.cloudfront import Distribution, DistributionConfig, ForwardedValues, Origin, CustomOriginConfig, \
    ViewerCertificate, DefaultCacheBehavior, S3OriginConfig
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget

template = Template(Description='Video CDN for spunt.be')

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

video_engine_stack = template.add_parameter(Parameter(
    'VideoEngineStack',
    Type=constants.STRING,
    Default='spunt-video-engine',
))

domain_name = template.add_parameter(Parameter(
    'DomainName',
    Type=constants.STRING,
    Default='videos.spunt.be',
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

video_cdn = template.add_resource(Distribution(
    "VideoDistribution",
    DistributionConfig=DistributionConfig(
        Aliases=[Ref(domain_name)],
        Comment=Ref(AWS_STACK_NAME),
        DefaultCacheBehavior=DefaultCacheBehavior(
            TargetOriginId='S3',
            ViewerProtocolPolicy='redirect-to-https',
            AllowedMethods=['GET', 'HEAD', 'OPTIONS'],
            CachedMethods=['GET', 'HEAD', 'OPTIONS'],
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
            Id='S3',
            DomainName=Join('', [
                ImportValue(Join('-', [Ref(video_engine_stack), 'VideoBucket', 'Ref'])),
                '.s3.',
                Ref(AWS_REGION),
                '.amazonaws.com'
            ]),
            S3OriginConfig=S3OriginConfig(
                OriginAccessIdentity=Join('', [
                    'origin-access-identity/cloudfront/',
                    ImportValue(Join('-', [Ref(video_engine_stack), 'VideoOriginAccessIdentity', 'Ref'])),
                ]),
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
            DNSName=GetAtt(video_cdn, 'DomainName'),
        ),
    ), RecordSet(
        Name=Ref(domain_name),
        Type='AAAA',
        AliasTarget=AliasTarget(
            HostedZoneId='Z2FDTNDATAQYW2',
            DNSName=GetAtt(video_cdn, 'DomainName'),
        ),
    )],
    Comment=Join('', ['Record for CloudFront in ', Ref(AWS_STACK_NAME)]),
))

f = open("output/video_cdn.json", "w")
f.write(template.to_json())
