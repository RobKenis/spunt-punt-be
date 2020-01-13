import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { AuthService } from "../../services/AuthService";
import "./SignUp.scss";

export class SignUp extends Component {
  state = {
    email: "",
  };

  handleEmailChange(e) {
    this.setState({ email: e.target.value });
  }

  handleSubmit(e) {
    e.preventDefault();
    const authService = new AuthService();
    authService.signUp(this.state.email);
  }

  render() {
    return (
      <section className="container section sign-up">
        <h1 className="title">Sign Up</h1>
        <form className="sign-up__form" onSubmit={this.handleSubmit.bind(this)}>
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
            <div className="control">
              <button className="button is-link">Sign Up</button>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
