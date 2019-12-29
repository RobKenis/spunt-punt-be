import React, { Component } from "react";
import "./NavBar.scss";

export class NavBar extends Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      toggled: false,
    };
  }

  toggle = () => {
    this.setState({
      toggled: !this.state.toggled,
    });
  };

  isToggled = () => {
    return this.state.toggled;
  };

  render() {
    return (
      <nav className="navbar is-black is-spaced">
        <div className="container">
          <div className="navbar-brand">
            <a className="navbar-item navbar-icon" href="/">
              S<span>.</span>
            </a>
            <div className={`navbar-burger burger ${this.isToggled() ? "is-active" : ""}`} onClick={this.toggle}>
              <span aria-hidden="true" />
              <span aria-hidden="true" />
              <span aria-hidden="true" />
            </div>
          </div>
          <div className={`navbar-menu ${this.isToggled() ? "is-active" : ""}`}>
            <div className="navbar-start">
              <a className="navbar-item" href="/">
                Home
              </a>
            </div>
            <div className="navbar-end">
              <div className="navbar-item">
                <a className="button is-light is-outlined" href="/sign-up">
                  Sign up
                </a>
              </div>
              <div className="navbar-item">
                <a className="button is-light" href="/log-in">
                  Log in
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>
    );
  }
}
