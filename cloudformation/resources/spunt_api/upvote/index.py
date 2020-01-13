import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def handler(event, context):
    body = json.loads(event['body'])
    if 'videoId' in body and 'userId' in body:
        # Add some validation on existing videoId or something.
        dynamo.put_item(
            TableName=VIDEO_EVENTS_TABLE,
            Item={
                'videoId': {'S': body['videoId']},
                'type': {'S': 'VIDEO_UPVOTED'},
                'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                'metadata': {'S': json.dumps({'userId': body['userId']})}
            }
        )
        print("Saved upvote event for [{video}] by [{user}]".format(video=body['videoId'], user=body['userId']))
        return {
            'statusCode': "200",
            'body': json.dumps({}),
            "isBase64Encoded": False,
        }
    else:
        print("VideoId and/or UserId not present.")
        return {
            'statusCode': "400",
            'body': json.dumps({}),
            "isBase64Encoded": False,
        }
