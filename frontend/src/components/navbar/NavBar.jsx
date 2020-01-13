import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHome, faFire, faBolt } from "@fortawesome/free-solid-svg-icons";
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
            <a className="navbar-item navbar-brand-icon" href="/">
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
                <FontAwesomeIcon icon={faHome} size="sm" className="navbar-item-icon" fixedWidth /> Home
              </a>
              <a className="navbar-item" href="/hot">
                <FontAwesomeIcon icon={faFire} size="sm" className="navbar-item-icon" fixedWidth /> Hot
              </a>
              <a className="navbar-item" href="/trending">
                <FontAwesomeIcon icon={faBolt} size="sm" className="navbar-item-icon" fixedWidth /> Trending
              </a>
              <div className="navbar-item">
                <a className="button is-light" href="/upload">
                  Upload
                </a>
              </div>
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
