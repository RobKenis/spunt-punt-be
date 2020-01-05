'use strict';

exports.handler = (event, context, callback) => {
    const request = event.Records[0].cf.request;
    request.uri = '/v1/upvote';

    return callback(null, request);
};
