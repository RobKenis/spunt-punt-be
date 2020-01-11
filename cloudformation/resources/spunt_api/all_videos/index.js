const AWS = require('aws-sdk');

AWS.config.update({region: 'us-east-1'});
const documentClient = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context, callback) => {
    const request = event.Records[0].cf.request;
    const videoTable = request.origin.custom.customHeaders["x-video-table"][0].value;
    const {Items: items} = await documentClient.query({
        TableName: videoTable,
        IndexName: 'lastModifiedInState',
        KeyConditionExpression: 'videoState = :state',
        ExpressionAttributeValues: {
            ':state': 'AVAILABLE'
        },
        Limit: 20,
        ScanIndexForward: false,
    }).promise();
    const videos = items.map(item => {
        const {lastModified, videoState, ...video} = item;
        return video;
    });
    const response = {
        status: "200",
        statusDescription: "OK",
        body: JSON.stringify({videos: videos}),
        headers: {
            "access-control-allow-origin": [{key: "Access-Control-Allow-Origin", value: "*"}],
            "access-control-allow-methods": [{key: "Access-Control-Allow-Methods", value: "GET, HEAD, OPTIONS"}],
            "access-control-max-age": [{key: "Access-Control-Max-Age", value: "86400"}]
        }
    };
    callback(null, response);
};
