import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME')

client = boto3.client('events')
dynamo = boto3.client('dynamodb')


def handler(event, context):
    for record in event['Records']:
        body = record['body']
        message = json.loads(body)['Message']
        payload = json.loads(message)['responsePayload']
        for msg in json.loads(payload['body'])['messages']:
            client.put_events(
                Entries=[
                    {
                        'Source': 'spunt.video.events',
                        'DetailType': 'metadata.start',
                        'Detail': json.dumps(msg),
                        'EventBusName': EVENT_BUS_NAME
                    },
                ]
            )
            dynamo.put_item(
                TableName=VIDEO_EVENTS_TABLE,
                Item={
                    'videoId': {'S': msg['videoId']},
                    'type': {'S': 'METADATA_FLOW_STARTED'},
                    'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                    'metadata': {'S': json.dumps({})}
                }
            )
