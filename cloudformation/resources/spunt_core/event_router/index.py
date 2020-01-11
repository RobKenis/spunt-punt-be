import json
import os

import boto3

client = boto3.client('sqs')

API_EVENTS_QUEUE_URL = os.environ.get('API_EVENTS_QUEUE_URL')
DASHBOARD_EVENTS_QUEUE_URL = os.environ.get('DASHBOARD_EVENTS_QUEUE_URL')


def handler(event, context):
    for record in event['Records']:
        if record['eventName'] is not 'REMOVE':
            try:
                event_data = record['dynamodb']['NewImage']
                for queue_url in [API_EVENTS_QUEUE_URL, DASHBOARD_EVENTS_QUEUE_URL]:
                    client.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps({
                            'videoId': event_data['videoId']['S'],
                            'timestamp': event_data['timestamp']['S'],
                            'type': event_data['type']['S'],
                            'metadata': event_data['metadata']['S']
                        }),
                    )
            except Exception as e:
                print("Failed to route event with id: [{id}]. Exception: {e}".format(id=record['eventID'], e=str(e)))
