import collections
import json

import boto3

rekognition = boto3.client('rekognition')


def handler(event, context):
    response = rekognition.get_label_detection(
        JobId='f714a7a0774c3a94fbe1a901dc6b8b4c5c03f7a85ffbfede925320d638175d73',
        SortBy='NAME'
    )
    count = collections.Counter([label['Label']['Name'] for label in response['Labels']])
    print(count)


handler(None, None)
