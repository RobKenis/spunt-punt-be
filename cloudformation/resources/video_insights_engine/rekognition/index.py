import json

import boto3

rekognition = boto3.client('rekognition')


def handler(event, context):
    response = rekognition.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': 'spunt-video-encoding-engine-upload',
                'Name': 'upload/BigBuckBunny_320x180.mp4',
            }
        },
        ClientRequestToken='ze-video-id',
        MinConfidence=70,
        # NotificationChannel={
        #     'SNSTopicArn': 'string',
        #     'RoleArn': 'string'
        # },
        JobTag='ze-video-id'
    )
    print(response)


handler(None, None)
