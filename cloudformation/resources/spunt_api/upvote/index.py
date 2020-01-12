import datetime
import json
import os

import boto3

VIDEO_EVENTS_TABLE = os.environ.get('VIDEO_EVENTS_TABLE')

dynamo = boto3.client('dynamodb')


def handler(event, context):
    if 'videoId' in event and 'userId' in event:
        # Add some validation on existing videoId or something.
        dynamo.put_item(
            TableName=VIDEO_EVENTS_TABLE,
            Item={
                'videoId': {'S': event['videoId']},
                'type': {'S': 'VIDEO_UPVOTED'},
                'timestamp': {'S': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()},
                'metadata': {'S': json.dumps({'userId': event['userId']})}
            }
        )
        print("Saved upvote event for [{video}] by [{user}]".format(video=event['videoId'], user=event['userId']))
        return {
            'status': "200",
            'statusDescription': "OK",
        }
    else:
        print("VideoId and/or UserId not present.")
        return {
            'status': "400",
            'statusDescription': "Bad request",
        }
