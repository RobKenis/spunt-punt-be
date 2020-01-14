import json


def handler(event, context):
    return {
        'statusCode': "200",
        'body': json.dumps({}),
        "isBase64Encoded": False,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, PUT, POST, DELETE, OPTIONS',
            'Access-Control-Max-Age': '86400',
        },
    }
