import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')
PIPELINE_ID_PARAMETER = os.environ.get('PIPELINE_ID_PARAMETER')

client = boto3.client('elastictranscoder')
dynamo = boto3.client('dynamodb')
ssm = boto3.client('ssm')

parameter_response = ssm.get_parameter(
    Name=PIPELINE_ID_PARAMETER,
    WithDecryption=False
)
PIPELINE_ID = parameter_response['Parameter']['Value']


def _store_event(video_id, status):
    dynamo.put_item(
        TableName=VIDEO_EVENTS_TABLE,
        Item={
            'videoId': {'S': video_id},
            'type': {'S': 'ENCODING_REQUESTED'},
            'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
            'metadata': {'S': json.dumps({
                'status': status,
            })}
        }
    )


def _request_encode(video_id, path):
    print("Requesting encode for [{videoId}] on path: {path}".format(videoId=video_id, path=path))
    response = client.create_job(
        PipelineId=PIPELINE_ID,
        Inputs=[{
            'Key': path,
            'FrameRate': 'auto',
            'Resolution': 'auto',
            'AspectRatio': 'auto',
            'Interlaced': 'auto',
            'Container': 'auto',
        }],
        Outputs=[{
            'Key': 'mpd-video',
            'PresetId': '1351620000001-500040',
            'SegmentDuration': '4.0',
        }, {
            'Key': 'mpd-audio',
            'PresetId': '1351620000001-500060',
            'SegmentDuration': '4.0',
        }],
        OutputKeyPrefix="{videoId}/".format(videoId=video_id),
        Playlists=[{
            'Name': video_id,
            'Format': 'MPEG-DASH',
            'OutputKeys': [
                'mpd-video',
                'mpd-audio',
            ],
        }],
        UserMetadata={
            'videoId': video_id
        }
    )
    _store_event(video_id, response['Job']['Status'])


def handler(event, context):
    for record in event['Records']:
        print("Handling message with id: [{eventId}]".format(eventId=record['Sns']['MessageId']))
        msg = json.loads(record['Sns']['Message'])
        for message in json.loads(msg['responsePayload']['body'])['messages']:
            _request_encode(message['videoId'], message['path'])
