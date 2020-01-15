from troposphere import GetAtt, Join, Output, Not, Equals, Parameter, Ref, Template, AWSObject, \
    AWSProperty, AWS_STACK_NAME, ImportValue, constants
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.cognito import UserPool, UserPoolClient, Policies, PasswordPolicy, SchemaAttribute
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

template = Template(Description='Cognito with passwordless e-mail auth')
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
    Default='login.spunt.be',
))

cognito_domain_name = template.add_parameter(Parameter(
    'CognitoDomainName',
    Type=constants.STRING,
    Default='',
    Description='Used for the A record since DomainName doesnt return its domain..'
))

DOMAIN_IS_CREATED = 'DomainIsCreated'
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

user_pool = template.add_resource(UserPool(
    'UserPool',
    UserPoolName=Ref(AWS_STACK_NAME),
    MfaConfiguration='OFF',
    Policies=Policies(
        PasswordPolicy=PasswordPolicy(
            RequireLowercase=False,
            RequireSymbols=False,
            RequireNumbers=False,
            MinimumLength=8,
            RequireUppercase=False
        )
    ),
    UsernameAttributes=['email'],
    Schema=[
        SchemaAttribute(
            AttributeDataType='String',
            Required=True,
            Name='email',
            Mutable=True
        )
    ]
))

user_pool_client = template.add_resource(UserPoolClient(
    'UserPoolClient',
    GenerateSecret=False,
    ExplicitAuthFlows=[
        'ALLOW_USER_SRP_AUTH',
        'ALLOW_USER_PASSWORD_AUTH',
        'ALLOW_REFRESH_TOKEN_AUTH'
    ],
    UserPoolId=Ref(user_pool),
    ClientName='spunt-users',
))

user_pool_client_id = template.add_output(Output(
    'UserPoolClientId',
    Description='ID of the User Pool Client',
    Value=Ref(user_pool_client),
))

user_pool_id = template.add_output(Output(
    'UserPoolId',
    Description='ID of the User Pool',
    Value=Ref(user_pool),
))

f = open("output/spunt_auth.json", "w")
f.write(template.to_json())
