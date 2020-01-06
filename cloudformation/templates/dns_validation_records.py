from troposphere import Template, Parameter, constants, Ref, ImportValue, Join
from troposphere.route53 import RecordSetGroup, RecordSet

RECORDS = {
    '_aadf1927354323bb06fc14c09b832db9.spunt.be.':
        '_22d8e5703e27b0d967ba1f5221f8e7be.mzlfeqexyx.acm-validations.aws.',
    '_a7d41ed42e87702fb5ebf49d474086a2.videos.spunt.be.':
        '_e4893dee46cfc65097d053d48d011668.mzlfeqexyx.acm-validations.aws.',
    '_7c72059be53c034a76b7c714450b289f.login.spunt.be.':
        '_d3b6de5c096a463801dca57650b56a54.mzlfeqexyx.acm-validations.aws.',
    '_78e5bd14e69fa43b330422cb0cd508fb.api.spunt.be.':
        '_8a703f2dd4e2902fb3925da4f6635f11.mzlfeqexyx.acm-validations.aws.'
}

template = Template(Description='Spunt.be validation records')

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

_hosted_zone_id = ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneId']))

template.add_resource(RecordSetGroup(
    'ValidationRecords',
    HostedZoneId=_hosted_zone_id,
    Comment='Validation records for ACM',
    RecordSets=list(map(lambda name: RecordSet(
        Name=name,
        Type='CNAME',
        TTL=900,
        ResourceRecords=[RECORDS[name]],
    ), RECORDS.keys()))
))

f = open("output/validation_records.json", "w")
f.write(template.to_json())
