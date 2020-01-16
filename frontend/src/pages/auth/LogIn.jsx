import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faKey } from "@fortawesome/free-solid-svg-icons";
import "./auth.scss";

export class LogIn extends Component {
  state = {
    email: "",
    password: "",
  };

  componentDidMount() {
    if (this.props.location && this.props.location.state) {
      this.setState({ email: this.props.location.state.email });
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.location && this.props.location.state) {
      if (this.props.location.state.email !== prevProps.location.state.email) {
        this.setState({ email: this.props.location.state.email });
      }
    }
  }

  handleEmailChange(e) {
    this.setState({ email: e.target.value });
  }

  handlePasswordChange(e) {
    this.setState({ password: e.target.value });
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.authService.signIn(this.state.email, this.state.password).then(() => {
      this.props.setAuthenticated(true);
      this.props.history.push("/");
    });
  }

  render() {
    return (
      <section className="container container--small section">
        <h1 className="title">Log In</h1>
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
              <button className="button is-primary">Log In</button>
            </div>
            <div className="control">
              <a className="button is-primary is-outlined" href="/auth/sign-up">
                Not registered yet?
              </a>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
