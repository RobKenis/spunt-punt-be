from awacs.aws import Policy, Statement, Allow, Principal, Action
from troposphere import Template, Ref, iam, GetAtt, Join
from troposphere.iam import Role
from troposphere.s3 import Bucket, BucketPolicy

template = Template(Description='Personalize for spunt.be videos.')

data_source = template.add_resource(Bucket(
    'PersonalizeDataSource'
))

personalize_role = template.add_resource(Role(
    'PersonalizeRole',
    Path="/",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {"Service": ["personalize.amazonaws.com"]},
        }],
    },
    ManagedPolicyArns=['arn:aws:iam::aws:policy/service-role/AmazonPersonalizeFullAccess'],
    Policies=[iam.Policy(
        PolicyName="do-personalize-things",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": [
                    "s3:*",
                ],
                "Effect": "Allow",
                "Resource": [GetAtt(data_source, 'Arn'), Join('', [GetAtt(data_source, 'Arn'), '/*'])]
            }],
        })],
))

template.add_resource((BucketPolicy(
    "PersonalizeDataSourcePolicy",
    Bucket=Ref(data_source),
    PolicyDocument=Policy(
        Version='2012-10-17',
        Statement=[Statement(
            Sid='AllowPersonalize',
            Effect=Allow,
            Principal=Principal('Service', 'personalize.amazonaws.com'),
            Action=[Action('s3', '*')],
            Resource=[Join("", ["arn:aws:s3:::", Ref(data_source), "/*"]),
                      Join("", ["arn:aws:s3:::", Ref(data_source)])],
        )],
    ),
)))

f = open("output/spunt_video_personalization.json", "w")
f.write(template.to_json())
