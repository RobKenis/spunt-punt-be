const AWS = require('aws-sdk');

AWS.config.update({region: 'us-east-1'});
const documentClient = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context, callback) => {
    const request = event.Records[0].cf.request;
    const videoId = /[^/]*$/.exec(request.uri)[0];
    const videoTable = request.origin.custom.customHeaders["x-video-table"][0].value;
    const {Item: item} = await documentClient.get({TableName: videoTable, Key: {videoId: videoId}}).promise();
    const {lastModified, ...video} = item;
    const response = {
        status: "200",
        statusDescription: "OK",
        body: JSON.stringify(video),
        headers: {
            "access-control-allow-origin": [{key: "Access-Control-Allow-Origin", value: "*"}],
            "access-control-allow-methods": [{key: "Access-Control-Allow-Methods", value: "GET, HEAD, OPTIONS"}],
            "access-control-max-age": [{key: "Access-Control-Max-Age", value: "86400"}]
        }
    };
    callback(null, response);
};
