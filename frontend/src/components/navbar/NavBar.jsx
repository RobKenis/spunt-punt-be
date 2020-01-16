import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHome, faFire, faBolt, faUpload, faUser, faSignInAlt, faSignOutAlt } from "@fortawesome/free-solid-svg-icons";
import "./NavBar.scss";

export class NavBar extends Component {
  state = {
    toggled: false,
  };

  toggle() {
    this.setState({
      toggled: !this.state.toggled,
    });
  }

  isToggled() {
    return this.state.toggled;
  }

  render() {
    return (
      <nav className="navbar is-black is-spaced">
        <div className="container">
          <div className="navbar-brand">
            <a className="navbar-item navbar-brand-icon" href="/">
              S<span>.</span>
            </a>
            <div
              className={`navbar-burger burger ${this.isToggled() ? "is-active" : ""}`}
              onClick={this.toggle.bind(this)}
            >
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
            </div>
            <div className="navbar-end">
              {this.props.isAuthenticated() ? (
                <>
                  <div className="navbar-item">
                    <a className="button is-primary" href="/upload">
                      <FontAwesomeIcon icon={faUpload} size="sm" className="navbar-item-icon" fixedWidth />
                      <span>Upload</span>
                    </a>
                  </div>
                  <div className="navbar-item">
                    <a className="button is-white" href="/auth/log-out">
                      <FontAwesomeIcon icon={faSignOutAlt} size="sm" className="navbar-item-icon" fixedWidth />
                      <span>Log out</span>
                    </a>
                  </div>
                </>
              ) : (
                <>
                  <div className="navbar-item">
                    <a className="button is-white is-outlined" href="/auth/sign-up">
                      <FontAwesomeIcon icon={faUser} size="sm" className="navbar-item-icon" fixedWidth />
                      <span>Sign Up</span>
                    </a>
                  </div>
                  <div className="navbar-item">
                    <a className="button is-white" href="/auth/log-in">
                      <FontAwesomeIcon icon={faSignInAlt} size="sm" className="navbar-item-icon" fixedWidth />
                      <span>Log In</span>
                    </a>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>
    );
  }
}
