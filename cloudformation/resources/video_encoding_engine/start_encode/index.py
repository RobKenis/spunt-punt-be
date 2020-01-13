import datetime
import json
import os
import re
import uuid

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')
VIDEO_ID_REGEX = r'^upload/([A-Za-z0-9\-]+)/.*mp4$'

dynamo = boto3.client('dynamodb')


def _is_valid_key(key):
    return bool(re.match(VIDEO_ID_REGEX, key))


def _save_dummy_created_event(video_id):
    dynamo.put_item(
        TableName=VIDEO_EVENTS_TABLE,
        Item={
            'videoId': {'S': video_id},
            'type': {'S': 'NEW_VIDEO_CREATED'},
            'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
            'metadata': {'S': json.dumps({'title': 'This is a dummy title', 'filename': 'dummy.mp4'})}
        }
    )
    print("DUMMY NEW_VIDEO_CREATED event for [{id}] saved.".format(id=video_id))


def _video_id(key):
    try:
        video_id = re.match(VIDEO_ID_REGEX, key).groups()[0]
        print("Extracted [{id}] from [{key}].".format(id=video_id, key=key))
        return video_id
    except AttributeError as e:
        print("Could not extract videoId from [{key}]".format(key=key))
        video_id = str(uuid.uuid1())
        _save_dummy_created_event(video_id)
        return video_id


def handler(event, context):
    videos = []
    for record in event['Records']:
        print("Handling message with id: [{eventId}]".format(eventId=record['Sns']['MessageId']))
        msg = json.loads(record['Sns']['Message'])
        for notification in msg['Records']:
            key = notification['s3']['object']['key']
            if _is_valid_key(key):
                video_id = _video_id(key)
                dynamo.put_item(
                    TableName=VIDEO_EVENTS_TABLE,
                    Item={
                        'videoId': {'S': video_id},
                        'type': {'S': 'NEW_VIDEO_UPLOADED'},
                        'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                        'metadata': {'S': json.dumps({
                            'bucket': notification['s3']['bucket']['name'],
                            'path': key,
                        })}
                    }
                )
                print("NEW_VIDEO_UPLOADED event for [{path}] saved.".format(path=key))
                videos.append({'videoId': video_id, 'path': key})
            else:
                print("Skipping [{key}].".format(key=key))
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
