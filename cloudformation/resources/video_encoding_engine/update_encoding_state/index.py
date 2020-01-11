import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def _store_event(video_id, status, metadata):
    dynamo.put_item(
        TableName=VIDEO_EVENTS_TABLE,
        Item={
            'videoId': {'S': video_id},
            'type': {'S': status},
            'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
            'metadata': {'S': json.dumps(metadata)}
        }
    )


def _encoding_started(video_id):
    _store_event(video_id, 'ENCODING_STARTED', {})


def _encoding_failed(video_id):
    _store_event(video_id, 'ENCODING_FAILED', {})


def _encoding_completed(video_id):
    _store_event(video_id, 'ENCODING_COMPLETED', {
        'path': "{videoId}/{videoId}.mpd".format(videoId=video_id),
        'thumbnailPath': "{videoId}/thumbnail-00001.png".format(videoId=video_id),
    })


def handler(event, context):
    for record in event['Records']:
        print("Handling message with id: [{eventId}]".format(eventId=record['Sns']['MessageId']))
        msg = json.loads(record['Sns']['Message'])
        print(msg)
        video_id = msg['userMetadata']['videoId']
        state = msg['state']
        print("Video with id: [{videoId}] is in state: [{state}]".format(videoId=video_id, state=state))
        switch = {
            'ERROR': _encoding_failed,
            'PROGRESSING': _encoding_started,
            'COMPLETED': _encoding_completed
        }
        state_handler = switch.get(state, lambda: "Invalid state")
        state_handler(video_id)
