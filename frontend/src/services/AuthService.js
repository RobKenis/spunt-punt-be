import Amplify, { Auth } from "aws-amplify";

Amplify.configure({
  Auth: {
    region: "us-east-1",
    userPoolId: "us-east-1_4G2G3t93q",
    userPoolWebClientId: "7o4ffpnvmhksc7goees8h54oqa",
  },
});

export class AuthService {
  cognitoUser;

  async signIn(email, password) {
    try {
      this.cognitoUser = await Auth.signIn(email, password);
      return Promise.resolve(this.cognitoUser);
    } catch (err) {
      return Promise.reject(err);
    }
  }

  async signOut() {
    try {
      await Auth.signOut();
      this.cognitoUser = null;
    } catch (err) {
      console.error(err);
    }
  }

  async signUp(email, password) {
    try {
      return await Auth.signUp({
        username: email,
        password: password,
      });
    } catch (err) {
      console.error(err);
    }
  }

  async confirmSignUp(email, code) {
    try {
      return await Auth.confirmSignUp(email, code);
    } catch (err) {
      console.error(err);
    }
  }

  async isAuthenticated() {
    try {
      if (this.cognitoUser) {
        return true;
      }
      await Auth.currentSession({});
      return true;
    } catch (err) {
      return false;
    }
  }

  async getUserDetails() {
    try {
      if (!this.cognitoUser) {
        this.cognitoUser = await Auth.currentAuthenticatedUser();
      }
      return await Auth.userAttributes(this.cognitoUser);
    } catch (err) {
      console.error(err);
    }
  }
}
