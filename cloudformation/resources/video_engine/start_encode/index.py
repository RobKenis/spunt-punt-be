import datetime
import json
import os
import uuid

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def handler(event, context):
    videos = []
    for record in event['Records']:
        print("Handling message with id: [{eventId}]".format(eventId=record['Sns']['MessageId']))
        msg = json.loads(record['Sns']['Message'])
        for notification in msg['Records']:
            video_id = str(uuid.uuid1())
            dynamo.put_item(
                TableName=VIDEO_EVENTS_TABLE,
                Item={
                    'videoId': {'S': video_id},
                    'type': {'S': 'NEW_VIDEO_UPLOADED'},
                    'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                    'metadata': {'S': json.dumps({
                        'bucket': notification['s3']['bucket']['name'],
                        'path': notification['s3']['object']['key'],
                    })}
                }
            )
            print("NEW_VIDEO_UPLOADED event for [{path}] saved.".format(path=notification['s3']['object']['key']))
            videos.append({'videoId': video_id, 'path': notification['s3']['object']['key']})
    return {
        'statusCode': 200,
        'body': json.dumps({
            'messages': list(map(lambda x: {
                'videoId': x['videoId'],
                'path': x['path'],
                'status': 'NEW_VIDEO_UPLOADED'
            }, videos))
        })
    }
