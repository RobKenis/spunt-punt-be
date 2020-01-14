import datetime
import json
import os
import uuid

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')
s3 = boto3.client('s3', region_name='us-east-1')

UPLOAD_REGION = 'us-east-1'  # Do not hard code, get from CloudFront-Viewer-Country header
UPLOAD_BUCKET = 'spunt-video-encoding-engine-upload'  # Do not hard code, get from SSM spunt/upload/region/bucket


# I'm very sorry for this piece of code. I'm not proud of it, this actually kind of makes me sad,
# but it's just the way it is. The people that created the SDK didn't really think this through.
def _generate_presigned_url(key):
    fields = {"acl": "bucket-owner-full-control"}

    conditions = [
        {"acl": "bucket-owner-full-control"},
        ["content-length-range", 1, 314572800]  # Max 30MB
    ]

    return s3.generate_presigned_post(
        Bucket=UPLOAD_BUCKET,
        Key=key,
        Fields=fields,
        Conditions=conditions
    )


def handler(event, context):
    body = json.loads(event['body'])
    if 'title' in body and 'filename' in body:
        video_id = str(uuid.uuid1())
        key = "upload/{videoId}/{filename}".format(videoId=video_id, filename=body['filename'])
        dynamo.put_item(
            TableName=VIDEO_EVENTS_TABLE,
            Item={
                'videoId': {'S': video_id},
                'type': {'S': 'NEW_VIDEO_CREATED'},
                'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                'metadata': {'S': json.dumps({'title': body['title'], 'filename': body['filename']})}
            }
        )
        print("Saved new video event for [{video}].".format(video=video_id))
        return {
            'statusCode': "201",
            'body': json.dumps({
                'videoId': video_id,
                'upload': _generate_presigned_url(key)
            }),
            "isBase64Encoded": False,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'GET, HEAD, PUT, POST, DELETE, OPTIONS',
                'Access-Control-Max-Age': '86400',
            },
        }
    else:
        print("Title and/or Filename not present.")
        return {
            'statusCode': "400",
            'body': json.dumps({}),
            "isBase64Encoded": False,
        }
