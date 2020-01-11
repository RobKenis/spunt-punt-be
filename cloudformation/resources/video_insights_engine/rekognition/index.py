import os

import boto3

rekognition = boto3.client('rekognition')

REKOGNITION_ROLE = os.environ.get('REKOGNITION_ROLE_ARN')
SNS_TOPIC = os.environ.get('REKOGNITION_UPDATES_TOPIC')
INPUT_BUCKET = os.environ.get('INPUT_BUCKET')


def handler(event, context):
    video_id = event['detail']['videoId']
    path = event['detail']['path']
    print("Starting Rekognition for {videoId} on path {path}".format(videoId=video_id, path=path))
    response = rekognition.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': INPUT_BUCKET,
                'Name': path,
            }
        },
        ClientRequestToken=video_id,
        MinConfidence=70,
        NotificationChannel={
            'SNSTopicArn': SNS_TOPIC,
            'RoleArn': REKOGNITION_ROLE,
        },
        JobTag=video_id
    )
    return {
        'videoId': video_id,
        'jobId': response['JobId'],
        'status': 'REKOGNITION_STARTED',
    }
