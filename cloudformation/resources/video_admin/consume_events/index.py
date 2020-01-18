import datetime
import json
import os

import boto3
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

VIDEO_TABLE = os.environ.get('VIDEO_TABLE')


def _error_handler(event):
    print("Cannot handle event with type: [{type}]".format(type=event['type']))


def _unsupported_event(event):
    print("Handler for event with type: [{type}] is not implemented.".format(type=event['type']))


def _new_video_created(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :lastModified, videoState = :state, title = :title",
            ConditionExpression="attribute_not_exists(videoId)",
            ExpressionAttributeValues={
                ':lastModified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':state': {
                    'S': 'NEW',
                },
                ':title': {
                    'S': json.loads(event['metadata'])['title'],
                },
            },
        )
        print("Saved new video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Did not save video with id [{id}] because item already exists.".format(id=event['videoId']))


def _new_video_uploaded(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :lastModified, videoState = :state",
            ConditionExpression="attribute_exists(videoId)",
            ExpressionAttributeValues={
                ':lastModified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':state': {
                    'S': 'PROCESSING',
                },
            },
        )
        print("Saved video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Video with id [{id}] not found to update.".format(id=event['videoId']))


def _encoding_completed(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :modified, videoState = :state",
            ConditionExpression="attribute_exists(videoId)",
            ExpressionAttributeValues={
                ':modified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':state': {
                    'S': 'AVAILABLE',
                },
            },
        )
        print("Saved video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Video with id [{id}] not found to update.".format(id=event['videoId']))


def _encoding_failed(event):
    try:
        client.update_item(
            TableName=VIDEO_TABLE,
            Key={
                'videoId': {'S': event['videoId']},
            },
            UpdateExpression="SET lastModified = :modified, videoState = :state",
            ConditionExpression="attribute_exists(videoId)",
            ExpressionAttributeValues={
                ':modified': {
                    'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
                },
                ':state': {
                    'S': 'FAILED',
                },
            },
        )
        print("Saved video with id: [{id}]".format(id=event['videoId']))
    except ClientError:
        print("Video with id [{id}] not found to update.".format(id=event['videoId']))


def handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        switch = {
            'NEW_VIDEO_CREATED': _new_video_created,
            'NEW_VIDEO_UPLOADED': _new_video_uploaded,
            'ENCODING_REQUESTED': _unsupported_event,
            'ENCODING_STARTED': _unsupported_event,
            'ENCODING_FAILED': _encoding_failed,
            'ENCODING_COMPLETED': _encoding_completed,
            'METADATA_FLOW_STARTED': _unsupported_event,
            'REKOGNITION_STARTED': _unsupported_event,
            'VIDEO_LABELS_COLLECTED': _unsupported_event,
            'VIDEO_UPVOTED': _unsupported_event,
        }
        event_handler = switch.get(body['type'], _error_handler)
        event_handler(body)
