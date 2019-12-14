import datetime
import json
import os
import uuid

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def handler(event, context):
    for record in event['Records']:
        print("Handling message with id: [{eventId}]".format(eventId=record['messageId']))
        sns_msg = json.loads(record['body'])
        msg = json.loads(sns_msg['Message'])
        for notification in msg['Records']:
            dynamo.put_item(
                TableName=VIDEO_EVENTS_TABLE,
                Item={
                    'videoId': {'S': str(uuid.uuid1())},
                    'type': {'S': 'NEW_VIDEO_UPLOADED'},
                    'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                    'metadata': {'S': json.dumps({
                        'bucket': notification['s3']['bucket']['name'],
                        'path': notification['s3']['object']['key'],
                    })}
                }
            )
            print("NEW_VIDEO_UPLOADED event for [{path}] saved.".format(path=notification['s3']['object']['key']))
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Events handled.'})
    }
