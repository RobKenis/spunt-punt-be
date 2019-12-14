from troposphere import Template, Ref, Join, AWS_STACK_NAME
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations, Filter, S3Key, Rules
from troposphere.sns import Topic, TopicPolicy

template = Template(Description='Video engine for spunt.be')

_upload_bucket_name = Join('-', [Ref(AWS_STACK_NAME), 'upload'])

upload_topic = template.add_resource(Topic(
    'UploadTopic',

))

template.add_resource(TopicPolicy(
    'UploadTopicPolicy',
    Topics=[Ref(upload_topic)],
    PolicyDocument={
        "Version": "2008-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "s3.amazonaws.com"},
                "Action": ["SNS:Publish"],
                "Resource": Ref(upload_topic),
                "Condition": {"ArnLike": {"aws:SourceArn": Join("", ["arn:aws:s3:::", _upload_bucket_name])}},
            },
        ],
    },
))

upload_bucket = template.add_resource(Bucket(
    'UploadBucket',
    BucketName=_upload_bucket_name,  # Setting the bucket name is stupid, but this resolves a circular dependency.
    NotificationConfiguration=NotificationConfiguration(
        TopicConfigurations=[TopicConfigurations(
            Event='s3:ObjectCreated:*',
            Filter=Filter(
                S3Key=S3Key(
                    Rules=[Rules(
                        Name='prefix',
                        Value='upload/',
                    )],
                ),
            ),
            Topic=Ref(upload_topic)
        )],
    ),
))

f = open("output/video_engine.json", "w")
f.write(template.to_json())
