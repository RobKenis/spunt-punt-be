import awacs
from awacs import aws, sts
from awacs.aws import Principal, Action
from troposphere import Template, GetAtt, Ref, Parameter, constants, AWS_STACK_NAME, Join
from troposphere.codebuild import Project, Artifacts, Source, Environment, EnvironmentVariable
from troposphere.codepipeline import Pipeline, Stages, Actions, ActionTypeId, ArtifactStore, OutputArtifacts, \
    InputArtifacts
from troposphere.iam import Role, Policy
from troposphere.s3 import Bucket

template = Template(Description="Code Pipeline for spunt.be")

github_user = template.add_parameter(Parameter(
    "GithubUser",
    Type=constants.STRING,
    Default='RobKenis'
))

github_token = template.add_parameter(Parameter(
    "GithubToken",
    Type=constants.STRING,
    NoEcho=True
))

github_repo = template.add_parameter(Parameter(
    "GithubRepo",
    Type=constants.STRING,
    Default='spunt-punt-be'
))

git_branch = template.add_parameter(Parameter(
    "GitBranch",
    Type=constants.STRING,
    Default='develop'
))

template.add_parameter_to_group(github_user, 'GitHub Settings')
template.add_parameter_to_group(github_repo, 'GitHub Settings')
template.add_parameter_to_group(github_token, 'GitHub Settings')
template.add_parameter_to_group(git_branch, 'GitHub Settings')

build_bucket = template.add_resource(Bucket(
    'BuildBucket',
))

pipeline_role = template.add_resource(Role(
    "CodePipelineRole",
    RoleName=Join("-", [Ref(AWS_STACK_NAME), "pipeline-role"]),
    AssumeRolePolicyDocument=awacs.aws.Policy(
        Statement=[
            awacs.aws.Statement(
                Effect=awacs.aws.Allow,
                Action=[awacs.sts.AssumeRole],
                Principal=Principal("Service", "codepipeline.amazonaws.com")
            ),
            awacs.aws.Statement(
                Effect=awacs.aws.Allow,
                Action=[awacs.sts.AssumeRole],
                Principal=Principal("Service", "cloudformation.amazonaws.com")
            ),
        ]
    ),
    Policies=[
        Policy(
            PolicyName='AllowS3',
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[Action("s3", "Put*"), Action("s3", "Get*")],
                        Resource=[
                            Join('', ["arn:aws:s3:::", Ref(build_bucket), "/*"]),
                            Join("", ["arn:aws:s3:::", Ref(build_bucket)]),
                        ],
                    )
                ]
            ),
        ),
        Policy(
            PolicyName='AllowCodeCommit',
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[Action("codecommit", "*")],
                        Resource=['*']
                    ),
                ]
            )
        ),
        Policy(
            PolicyName='AllowCodeBuild',
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[Action("codebuild", "*")],
                        Resource=['*']
                    ),
                ]
            )
        ),
        Policy(
            PolicyName='AllowCloudFormation',
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[
                            Action("cloudformation", "*"),
                            Action("sts", "AssumeRole"),
                            Action("iam", "PassRole"),
                        ],
                        Resource=['*'],
                    ),
                ]
            )
        ),
    ]
))

codebuild_role = template.add_resource(Role(
    "CodeBuildRole",
    RoleName=Join("-", [Ref(AWS_STACK_NAME), "build-role"]),
    AssumeRolePolicyDocument=awacs.aws.Policy(
        Statement=[
            awacs.aws.Statement(
                Effect=awacs.aws.Allow,
                Action=[awacs.sts.AssumeRole],
                Principal=Principal("Service", 'codebuild.amazonaws.com'),
            ),
        ]
    ),
    Policies=[
        Policy(
            PolicyName='AllowCodeBuild',
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[
                            Action("codebuild", "**"),
                            Action("logs", "**"),
                            Action("s3", "**"),
                        ],
                        Resource=['*']
                    )
                ]
            ),
        )
    ]
))

codebuild_project = template.add_resource(Project(
    "CodebuildProject",
    Name=Join("-", [Ref(AWS_STACK_NAME), "build-project"]),
    ServiceRole=GetAtt(codebuild_role, 'Arn'),
    Source=Source(
        Type='CODEPIPELINE',
    ),
    Artifacts=Artifacts(
        Type='CODEPIPELINE'
    ),
    Environment=Environment(
        Type='LINUX_CONTAINER',
        Image='aws/codebuild/amazonlinux2-x86_64-standard:2.0',
        ComputeType='BUILD_GENERAL1_SMALL',
        EnvironmentVariables=[EnvironmentVariable(
            Name='BUILD_BUCKET',
            Value=Ref(build_bucket),
        )]
    )
))

template.add_resource(Pipeline(
    "CodePipeline",
    Name=Ref(AWS_STACK_NAME),
    RoleArn=GetAtt(pipeline_role, 'Arn'),
    ArtifactStore=ArtifactStore(
        Type='S3',
        Location=Ref(build_bucket)
    ),
    Stages=[
        Stages(
            Name="Checkout",
            Actions=[
                Actions(
                    Name="CheckoutGithub",
                    ActionTypeId=ActionTypeId(
                        Category='Source',
                        Owner='ThirdParty',
                        Provider='GitHub',
                        Version='1'
                    ),
                    Configuration={
                        "Owner": Ref(github_user),
                        "Repo": Ref(github_repo),
                        "Branch": Ref(git_branch),
                        "OAuthToken": Ref(github_token),
                    },
                    OutputArtifacts=[
                        OutputArtifacts(
                            Name="SourceOutput"
                        )
                    ]
                )
            ]
        ),
        Stages(
            Name="Build",
            Actions=[
                Actions(
                    Name="Build",
                    ActionTypeId=ActionTypeId(
                        Category='Build',
                        Owner='AWS',
                        Provider='CodeBuild',
                        Version='1'
                    ),
                    InputArtifacts=[
                        InputArtifacts(
                            Name='SourceOutput'
                        )
                    ],
                    OutputArtifacts=[OutputArtifacts(
                        Name='BuildOutput',
                    )],
                    Configuration={
                        "ProjectName": Ref(codebuild_project),
                    }
                )
            ]
        ),
        Stages(
            Name='DeployCloudFormation',
            Actions=[
                Actions(
                    Name='CreateChangeSet',
                    ActionTypeId=ActionTypeId(
                        Category='Deploy',
                        Owner='AWS',
                        Provider='CloudFormation',
                        Version='1'
                    ),
                    InputArtifacts=[InputArtifacts(
                        Name='BuildOutput',
                    )],
                    Configuration={
                        'ActionMode': 'CHANGE_SET_REPLACE',
                        'StackName': 'spunt-punt-be',
                        'TemplatePath': 'BuildOutput::frontend_hosting.json',  # CHANGE THIS
                        'RoleArn': GetAtt(pipeline_role, 'Arn'),
                        'ChangeSetName': 'SpuntPuntBeChangeSet',
                    },
                    RoleArn=GetAtt(pipeline_role, 'Arn'),
                    RunOrder=1,
                ),
                Actions(
                    Name='ExecuteChangeSet',
                    ActionTypeId=ActionTypeId(
                        Category='Deploy',
                        Owner='AWS',
                        Provider='CloudFormation',
                        Version='1'
                    ),
                    InputArtifacts=[InputArtifacts(
                        Name='BuildOutput',
                    )],
                    Configuration={
                        'ActionMode': 'CHANGE_SET_EXECUTE',
                        'StackName': 'spunt-punt-be',
                        'ChangeSetName': 'SpuntPuntBeChangeSet',
                    },
                    RoleArn=GetAtt(pipeline_role, 'Arn'),
                    RunOrder=2,
                ),
            ],
        )
    ]
))

f = open("output/spunt_be_pipeline.json", "w")
f.write(template.to_json())
