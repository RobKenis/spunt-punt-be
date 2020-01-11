import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def handler(event, context):
    dynamo.put_item(
        TableName=VIDEO_EVENTS_TABLE,
        Item={
            'videoId': {'S': event['videoId']},
            'type': {'S': event['status']},
            'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
            'metadata': {'S': json.dumps({})}
        }
    )
