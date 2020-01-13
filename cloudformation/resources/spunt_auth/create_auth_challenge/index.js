const crypto = require('crypto');
const AWS = require('aws-sdk');

const ses = new AWS.SES();

const randomDigit = () => {
  let randomNumber;
  while (true) {
    randomNumber = crypto.randomBytes(1)[0];
    if (randomNumber < 250) {
      return randomNumber % 10;
    }
  }
};

const randomDigits = (nr) => {
  return [...Array(nr)].map(() => randomDigit());
};

const sendEmail = async (emailAddress, secretLoginCode) => {
  const params = {
    Destination: {ToAddresses: [emailAddress]},
    Message: {
      Body: {
        Html: {
          Charset: 'UTF-8',
          Data: `
            <html lang="en">
            <body>
              <p>This is your secret login code:</p>
              <h3>${secretLoginCode}</h3>
            </body>
            </html>`
        },
        Text: {
          Charset: 'UTF-8',
          Data: `Your secret login code: ${secretLoginCode}`
        }
      },
      Subject: {
        Charset: 'UTF-8',
        Data: 'Your secret login code'
      }
    },
    Source: process.env.SES_FROM_ADDRESS
  };
  await ses.sendEmail(params).promise();
};

exports.handler = async event => {
  let secretLoginCode;
  if (!event.request.session || !event.request.session.length) {
    secretLoginCode = randomDigits(6).join('');
    await sendEmail(event.request.userAttributes.email, secretLoginCode);
  } else {
    const previousChallenge = event.request.session.slice(-1)[0];
    secretLoginCode = previousChallenge.challengeMetadata.match(/CODE-(\d*)/)[1];
  }

  event.response.publicChallengeParameters = {email: event.request.userAttributes.email};
  event.response.privateChallengeParameters = {secretLoginCode};
  event.response.challengeMetadata = `CODE-${secretLoginCode}`;

  return event;
};
