exports.handler = (event, context, callback) => {
    const response = {
        status: '200',
        statusDescription: 'OK',
        body: "Lambda@Edge is awesome!",
    };
    callback(null, response);
};
