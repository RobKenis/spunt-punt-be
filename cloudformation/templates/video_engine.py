from troposphere import Template, Ref, Join, AWS_STACK_NAME, GetAtt
from troposphere.s3 import Bucket, NotificationConfiguration, TopicConfigurations, Filter, S3Key, Rules
from troposphere.sns import Topic, TopicPolicy, Subscription
from troposphere.sqs import Queue, QueuePolicy

template = Template(Description='Video engine for spunt.be')

_upload_bucket_name = Join('-', [Ref(AWS_STACK_NAME), 'upload'])

encode_video_queue = template.add_resource(Queue(
    'EncodeVideoQueue'
))

upload_topic = template.add_resource(Topic(
    'UploadTopic',
    Subscription=[Subscription(
        Endpoint=GetAtt(encode_video_queue, 'Arn'),
        Protocol='SQS',
    )],
))

template.add_resource(QueuePolicy(
    "EncodeVideoQueuePolicy",
    Queues=[Ref(encode_video_queue)],
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(encode_video_queue, 'Arn'),
            "Principal": {"Service": "sns.amazonaws.com"},
            "Condition": {"ArnEquals": {"aws:SourceArn": Ref(upload_topic)}},
        }],
    },
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
