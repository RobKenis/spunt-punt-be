import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faKey } from "@fortawesome/free-solid-svg-icons";
import { AuthService } from "../../services/AuthService";
import "./auth.scss";

export class Confirm extends Component {
  authService;

  state = {
    code: "",
  };

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
  }

  handleCodeChange(e) {
    this.setState({ code: e.target.value.trim() });
  }

  handleSubmit(e) {
    e.preventDefault();
    this.authService.confirmSignUp(this.props.location.state.email, this.state.code).then(() => {
      this.props.history.push("/auth/log-in", {
        email: this.props.location.state.email,
      });
    });
  }

  render() {
    return (
      <section className="container container--small section">
        <h1 className="title">Confirm account</h1>
        <form className="form" onSubmit={this.handleSubmit.bind(this)}>
          <div className="field">
            <div className="control has-icons-left">
              <input
                type="number"
                className="input"
                value={this.state.code}
                onChange={this.handleCodeChange.bind(this)}
              />
              <span className="icon is-small is-left">
                <FontAwesomeIcon icon={faKey} size="sm" fixedWidth />
              </span>
            </div>
          </div>
          <div className="field">
            <div className="control">
              <button className="button is-primary">Confirm</button>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
