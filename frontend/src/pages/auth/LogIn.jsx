import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import "./LogIn.scss";

export class LogIn extends Component {
  state = {
    email: "",
  };

  handleEmailChange(e) {
    this.setState({ email: e.target.value });
  }

  render() {
    return (
      <section className="container section log-in">
        <h1 className="title">Log In</h1>
        <form className="log-in__form">
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
              <button className="button is-link">Log In</button>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
