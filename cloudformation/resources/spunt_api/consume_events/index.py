import datetime
import json
import os

import boto3
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

VIDEO_TABLE = os.environ.get('VIDEO_TABLE')

VIDEO_URL = "https://videos.spunt.be/{path}"
THUMBNAIL_URL = "https://videos.spunt.be/{path}"  # Put this on a different CDN.


def _error_handler(event):
    print("Cannot handle event with type: [{type}]".format(type=event['type']))


def _unsupported_event(event):
    print("Handler for event with type: [{type}] is not implemented.".format(type=event['type']))


def _new_video_uploaded(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :lastModified",
            ConditionExpression="attribute_not_exists(videoId)",
            ExpressionAttributeValues={
                ':lastModified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
            },
        )
        print("Saved new video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Did not save video with id [{id}] because item already exists.".format(id=event['videoId']))


def _encoding_completed(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :modified, playbackUrl = :playback, thumbnailUrl = :thumbnail",
            ConditionExpression="attribute_exists(videoId)",
            ExpressionAttributeValues={
                ':modified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':playback': {
                    'S': VIDEO_URL.format(path=json.loads(event['metadata'])['path']),
                },
                ':thumbnail': {
                    'S': THUMBNAIL_URL.format(path=json.loads(event['metadata'])['thumbnailPath']),
                },
            },
        )
        print("Saved new video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Video with id [{id}] not found to update.".format(id=event['videoId']))


def _video_labels_collected(event):
    labels = json.loads(event['metadata'])['labels']
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :lastModified, labels = :labels",
            ConditionExpression="attribute_exists(videoId)",
            ExpressionAttributeValues={
                ':lastModified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':labels': {
                    'L': list(map(lambda label: {'S': label['name']}, labels[:5]))
                }
            },
        )
        print("Saved new video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Video with id [{id}] not found to update.".format(id=event['videoId']))


def handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        switch = {
            'NEW_VIDEO_UPLOADED': _new_video_uploaded,
            'ENCODING_REQUESTED': _unsupported_event,
            'ENCODING_STARTED': _unsupported_event,
            'ENCODING_FAILED': _unsupported_event,
            'ENCODING_COMPLETED': _encoding_completed,
            'METADATA_FLOW_STARTED': _unsupported_event,
            'REKOGNITION_STARTED': _unsupported_event,
            'VIDEO_LABELS_COLLECTED': _video_labels_collected,
        }
        event_handler = switch.get(body['type'], _error_handler)
        event_handler(body)
