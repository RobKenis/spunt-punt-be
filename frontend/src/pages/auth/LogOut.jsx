import React, { Component } from "react";
import { AuthService } from "../../services/AuthService";
import "./auth.scss";

export class LogOut extends Component {
  authService;

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
  }

  componentDidMount() {
    this.authService.signOut().then(() => {
      this.props.setAuthenticated(false);
      this.props.history.push("/");
    });
  }

  render() {
    return <></>;
  }
}
