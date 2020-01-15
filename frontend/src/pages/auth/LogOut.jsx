import React, { Component } from "react";
import "./auth.scss";

export class LogOut extends Component {
  componentDidMount() {
    this.props.authService.signOut().then(() => {
      this.props.setAuthenticated(false);
      this.props.history.push("/");
    });
  }

  render() {
    return <></>;
  }
}
