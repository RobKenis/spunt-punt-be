import collections
import datetime
import json
import os

import boto3

rekognition = boto3.client('rekognition')
dynamo = boto3.client('dynamodb')

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')


def handler(event, context):
    response = rekognition.get_label_detection(
        JobId=event['jobId'],
        SortBy='NAME'
    )
    print("Job with id: {id} finished with status: {status}.".format(id=event['jobId'], status=response['JobStatus']))
    counter = collections.Counter([label['Label']['Name'] for label in response['Labels']])
    labels = list(map(lambda count: {'name': count[0], 'amount': count[1]}, counter.most_common()))
    dynamo.put_item(
        TableName=VIDEO_EVENTS_TABLE,
        Item={
            'videoId': {'S': event['videoId']},
            'type': {'S': 'VIDEO_LABELS_COLLECTED'},
            'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
            'metadata': {'S': json.dumps({'labels': labels})}
        }
    )
