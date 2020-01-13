from troposphere import GetAtt, Join, Output, Not, Equals, Parameter, Ref, Template, AWSObject, \
    AWSProperty, AWS_STACK_NAME, ImportValue
from troposphere.awslambda import Environment, Permission
from troposphere.cognito import UserPool, UserPoolClient, Policies, PasswordPolicy, SchemaAttribute, LambdaConfig
from troposphere.iam import Policy, PolicyType, Role
from troposphere.serverless import Function, S3Location


template = Template(Description='Cognito with passwordless e-mail auth')
template.set_transform('AWS::Serverless-2016-10-31')

core_stack = template.add_parameter(Parameter(
    'CoreStack',
    Type='String',
    Default='spunt-core',
))

ses_from_address = template.add_parameter(Parameter(
    'SESFromAddress',
    Type='String',
    Default='noreply@spunt.be',
    Description='The e-mail address to send the secret login code from',
))

create_auth_challenge_lambda_code_key = template.add_parameter(Parameter(
    'CreateAuthChallenge',
    Type='String',
    Default='lambda-code/auth/create_auth_challenge.zip',
))

verify_auth_challenge_response_lambda_code_key = template.add_parameter(Parameter(
    'VerifyAuthChallengeResponse',
    Type='String',
    Default='lambda-code/auth/verify_auth_challenge_response.zip',
))

pre_sign_up_lambda_code_key = template.add_parameter(Parameter(
    'PreSignUp',
    Type='String',
    Default='lambda-code/auth/pre_sign_up.zip',
))

post_authentication_lambda_code_key = template.add_parameter(Parameter(
    'PostAuthentication',
    Type='String',
    Default='lambda-code/auth/post_authentication.zip',
))

define_auth_challenge_lambda_code_key = template.add_parameter(Parameter(
    'DefineAuthChallenge',
    Type='String',
    Default='lambda-code/auth/define_auth_challenge.zip',
))

template.add_parameter_to_group(create_auth_challenge_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(verify_auth_challenge_response_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(pre_sign_up_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(post_authentication_lambda_code_key, 'Lambda Keys')
template.add_parameter_to_group(define_auth_challenge_lambda_code_key, 'Lambda Keys')

create_auth_challenge = template.add_resource(Function(
    'CreateAuthChallengeFunction',
    Environment=Environment(
        Variables={'SES_FROM_ADDRESS': Ref(ses_from_address)}
    ),
    Handler='index.handler',
    Policies=[{
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': ['ses:SendEmail'],
                'Resource': '*',
                'Effect': 'Allow'
            }
        ]
    }],
    Runtime='nodejs10.x',
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(create_auth_challenge_lambda_code_key),
    ),
))

create_auth_challenge_invocation_permission = template.add_resource(Permission(
    'CreateAuthChallengeInvocationPermission',
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(create_auth_challenge, 'Arn'),
    SourceArn=GetAtt('UserPool', 'Arn'),
    Principal='cognito-idp.amazonaws.com',
))

verify_auth_challenge_response = template.add_resource(Function(
    'VerifyAuthChallengeResponseFunction',
    Handler='index.handler',
    Runtime='nodejs10.x',
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(verify_auth_challenge_response_lambda_code_key),
    ),
))

verify_auth_challenge_response_invocation_permission = template.add_resource(Permission(
    'VerifyAuthChallengeResponseInvocationPermission',
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(verify_auth_challenge_response, 'Arn'),
    SourceArn=GetAtt('UserPool', 'Arn'),
    Principal='cognito-idp.amazonaws.com',
))

pre_sign_up = template.add_resource(Function(
    'PreSignUpFunction',
    Handler='index.handler',
    Runtime='nodejs10.x',
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(pre_sign_up_lambda_code_key),
    ),
))

pre_sign_up_invocation_permission = template.add_resource(Permission(
    'PreSignUpInvocationPermission',
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(pre_sign_up, 'Arn'),
    SourceArn=GetAtt('UserPool', 'Arn'),
    Principal='cognito-idp.amazonaws.com',
))

post_authentication_role = template.add_resource(Role(
    'PostAuthenticationRole',
    ManagedPolicyArns=['arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'],
    AssumeRolePolicyDocument={
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': ['sts:AssumeRole'],
                'Effect': 'Allow',
                'Principal': { 'Service': ['lambda.amazonaws.com'] }
            }
        ]
    },
))

post_authentication = template.add_resource(Function(
    'PostAuthenticationFunction',
    Handler='index.handler',
    Role=GetAtt(post_authentication_role, 'Arn'),
    Runtime='nodejs10.x',
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(post_authentication_lambda_code_key),
    ),
))

post_authentication_invocation_permission = template.add_resource(Permission(
    'PostAuthenticationInvocationPermission',
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(post_authentication, 'Arn'),
    SourceArn=GetAtt('UserPool', 'Arn'),
    Principal='cognito-idp.amazonaws.com',
))

set_user_attributes_policy = template.add_resource(PolicyType(
    'SetUserAttributesPolicy',
    PolicyName='allow-set-user-attributes',
    PolicyDocument={
        'Version': '2012-10-17',
        'Statement': [
            {
                'Action': ['cognito-idp:AdminUpdateUserAttributes'],
                'Resource': [GetAtt('UserPool', 'Arn')],
                'Effect': 'Allow'
            }
        ]
    },
    Roles=[Ref(post_authentication_role)],
))

define_auth_challenge = template.add_resource(Function(
    'DefineAuthChallengeFunction',
    Handler='index.handler',
    Runtime='nodejs10.x',
    AutoPublishAlias='live',
    CodeUri=S3Location(
        Bucket=ImportValue(Join('-', [Ref(core_stack), 'LambdaCodeBucket-Ref'])),
        Key=Ref(define_auth_challenge_lambda_code_key),
    ),
))

define_auth_challenge_invocation_permission = template.add_resource(Permission(
    'DefineAuthChallengeInvocationPermission',
    Action='lambda:InvokeFunction',
    FunctionName=GetAtt(define_auth_challenge, 'Arn'),
    SourceArn=GetAtt('UserPool', 'Arn'),
    Principal='cognito-idp.amazonaws.com',
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
    ],
    LambdaConfig=LambdaConfig(
        PostAuthentication=GetAtt(post_authentication, 'Arn'),
        DefineAuthChallenge=GetAtt(define_auth_challenge, 'Arn'),
        CreateAuthChallenge=GetAtt(create_auth_challenge, 'Arn'),
        VerifyAuthChallengeResponse=GetAtt(verify_auth_challenge_response, 'Arn'),
        PreSignUp=GetAtt(pre_sign_up, 'Arn')
    ),
))

user_pool_client = template.add_resource(UserPoolClient(
    'UserPoolClient',
    GenerateSecret=False,
    ExplicitAuthFlows=['CUSTOM_AUTH_FLOW_ONLY'],
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
