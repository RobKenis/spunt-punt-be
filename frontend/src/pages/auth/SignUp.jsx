import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faKey } from "@fortawesome/free-solid-svg-icons";
import "./auth.scss";

export class SignUp extends Component {
  state = {
    email: "",
    password: "",
  };

  handleEmailChange(e) {
    this.setState({ email: e.target.value });
  }

  handlePasswordChange(e) {
    this.setState({ password: e.target.value });
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.authService.signUp(this.state.email, this.state.password).then((response) => {
      this.props.history.push("/auth/confirm", {
        email: response.user.username,
      });
    });
  }

  render() {
    return (
      <section className="container container--small section">
        <h1 className="title">Sign Up</h1>
        <form className="form" onSubmit={this.handleSubmit.bind(this)}>
          <div className="field">
            <div className="control has-icons-left">
              <input
                type="email"
                className="input"
                placeholder="E-mail"
                value={this.state.email}
                onChange={this.handleEmailChange.bind(this)}
              />
              <span className="icon is-small is-left">
                <FontAwesomeIcon icon={faEnvelope} size="sm" fixedWidth />
              </span>
            </div>
          </div>
          <div className="field">
            <div className="control has-icons-left">
              <input
                type="password"
                className="input"
                placeholder="Password"
                value={this.state.password}
                onChange={this.handlePasswordChange.bind(this)}
              />
              <span className="icon is-small is-left">
                <FontAwesomeIcon icon={faKey} size="sm" fixedWidth />
              </span>
            </div>
          </div>
          <div className="field is-grouped">
            <div className="control">
              <button className="button is-primary">Sign Up</button>
            </div>
            <div className="control">
              <a className="button is-primary is-outlined" href="/auth/log-in">
                Already have an account?
              </a>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
