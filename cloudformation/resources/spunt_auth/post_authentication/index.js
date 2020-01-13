const AWS = require('aws-sdk');

const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider();

exports.handler = async (event) => {
  if (event.request.userAttributes.email_verified !== 'true') {
    const params = {
      UserPoolId: event.userPoolId,
      UserAttributes: [{
        Name: 'email_verified',
        Value: 'true',
      }],
      Username: event.userName,
    };
    await cognitoIdentityServiceProvider.adminUpdateUserAttributes(params).promise();
  }
  return event;
};
