from troposphere import Template, AWS_STACK_NAME, Ref, AWSObject, AWSProperty, Parameter, constants, ImportValue, Join, \
    Equals, Not
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.cognito import UserPool
from troposphere.route53 import RecordSetGroup, RecordSet, AliasTarget


class CustomDomainConfig(AWSProperty):
    props = {
        'CertificateArn': (str, True),
    }


class UserPoolDomain(AWSObject):
    resource_type = "AWS::Cognito::UserPoolDomain"

    props = {
        'Domain': (str, True),
        'UserPoolId': (str, True),
        'CustomDomainConfig': (CustomDomainConfig, False),
    }


template = Template(Description='Cognito for spunt.be')

dns_stack = template.add_parameter(Parameter(
    'DnsStack',
    Type=constants.STRING,
    Default='spunt-punt-be-dns',
))

domain_name = template.add_parameter(Parameter(
    'DomainName',
    Type=constants.STRING,
    Default='login.spunt.be',
))

cognito_domain_name = template.add_parameter(Parameter(
    'CognitoDomainName',
    Type=constants.STRING,
    Default='',
    Description='Used for the A record since DomainName doesnt return its domain..'
))

DOMAIN_IS_CREATED='DomainIsCreated'
template.add_condition(DOMAIN_IS_CREATED, Not(Equals(Ref(cognito_domain_name), '')))

certificate = template.add_resource(Certificate(
    "Certificate",
    DomainName=Ref(domain_name),
    DomainValidationOptions=[DomainValidationOption(
        DomainName=Ref(domain_name),
        ValidationDomain=ImportValue(Join('-', [Ref(dns_stack), 'HostedZoneName'])),
    )],
    ValidationMethod='DNS',
))

user_pool = template.add_resource(UserPool(
    'CognitoUserPool',
    UserPoolName=Ref(AWS_STACK_NAME),
))

user_pool_domain = template.add_resource(UserPoolDomain(
    'UserPoolDomain',
    UserPoolId=Ref(user_pool),
    Domain=Ref(domain_name),
    CustomDomainConfig=CustomDomainConfig(
        CertificateArn=Ref(certificate),
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
            DNSName=Ref(cognito_domain_name),
        ),
    ), RecordSet(
        Name=Ref(domain_name),
        Type='AAAA',
        AliasTarget=AliasTarget(
            HostedZoneId='Z2FDTNDATAQYW2',
            DNSName=Ref(cognito_domain_name),
        ),
    )],
    Comment=Join('', ['Record for Cognito in ', Ref(AWS_STACK_NAME)]),
    Condition=DOMAIN_IS_CREATED,
))

f = open("output/spunt_auth.json", "w")
f.write(template.to_json())
