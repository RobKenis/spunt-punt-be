import datetime
import json
import os
import uuid

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')

UPLOAD_REGION = 'us-east-1'  # Do not hard code, get from CloudFront-Viewer-Country header
UPLOAD_BUCKET = 'spunt-video-encoding-engine-upload'  # Do not hard code, get from SSM spunt/upload/region/bucket


def handler(event, context):
    if 'title' in event and 'filename' in event:
        video_id = str(uuid.uuid1())
        dynamo.put_item(
            TableName=VIDEO_EVENTS_TABLE,
            Item={
                'videoId': {'S': video_id},
                'type': {'S': 'NEW_VIDEO_CREATED'},
                'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                'metadata': {'S': json.dumps({'title': event['title'], 'filename': event['filename']})}
            }
        )
        print("Saved new video event for [{video}].".format(video=video_id))
        return {
            'status': "200",
            'statusDescription': "OK",
            'body': json.dumps({
                'videoId': video_id,
                'metadata': {
                    'region': UPLOAD_REGION,
                    'bucket': UPLOAD_BUCKET,
                    'key': "upload/{videoId}/{filename}".format(videoId=video_id, filename=event['filename']),
                    'url': 'HERE_GOES_THE_PRESIGNED_URL',
                }
            }),
        }
    else:
        print("Title and/or Filename not present.")
        return {
            'status': "400",
            'statusDescription': "Bad request",
        }
