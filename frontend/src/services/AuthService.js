import { CognitoUserPool, CognitoUserAttribute } from "amazon-cognito-identity-js";

export class AuthService {
  userPool;

  constructor() {
    this.userPool = new CognitoUserPool({
      UserPoolId: "us-east-1_4G2G3t93q",
      ClientId: "7o4ffpnvmhksc7goees8h54oqa",
    });
  }

  signUp(email) {
    const attributeList = [
      new CognitoUserAttribute({
        Name: "email",
        Value: email.trim(),
      }),
    ];
    this.userPool.signUp(email.trim(), "weArePasswordless", attributeList, null, (err, result) => {
      console.log(result);
    });
  }
}
