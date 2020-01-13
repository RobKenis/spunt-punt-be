const MAX_AMOUNT_OF_ATTEMPTS = 3;

exports.handler = async (event) => {
  const maxAttemptsFailed = () => {
    return event.request.session
      && event.request.session.length >= MAX_AMOUNT_OF_ATTEMPTS
      && event.request.session.slice(-1)[0].challengeResult === false;
  };

  if (maxAttemptsFailed()) {
    event.response.issueTokens = false;
    event.response.failAuthentication = true;
    return event;
  }

  const isCorrectChallenge = () => {
    return event.request.session
      && event.request.session.length
      && event.request.session.slice(-1)[0].challengeResult === true;
  };

  if (isCorrectChallenge()) {
    event.response.issueTokens = true;
    event.response.failAuthentication = false;
    return event;
  }

  event.response.issueTokens = false;
  event.response.failAuthentication = false;
  event.response.challengeName = 'CUSTOM_CHALLENGE';
  return event;
};
