import React, { Component } from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { NavBar } from "./components/navbar/NavBar";
import { Home } from "./pages/overview/Home";
import { Hot } from "./pages/overview/Hot";
import { Trending } from "./pages/overview/Trending";
import { Upload } from "./pages/upload/Upload";
import { Detail } from "./pages/detail/Detail";
import { SignUp } from "./pages/auth/SignUp";
import { Confirm } from "./pages/auth/Confirm";
import { LogIn } from "./pages/auth/LogIn";
import { LogOut } from "./pages/auth/LogOut";
import { AuthService } from "./services/AuthService";

export class App extends Component {
  authService;

  state = {
    isAuthenticated: false,
  };

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
    this.setAuthenticated = this.setAuthenticated.bind(this);
  }

  componentDidMount() {
    this.authService.isAuthenticated().then((response) => {
      this.setState({ isAuthenticated: response });
    });
  }

  isAuthenticated() {
    return this.state.isAuthenticated;
  }

  setAuthenticated(value) {
    this.setState({ isAuthenticated: value });
  }

  render() {
    return (
      <>
        <NavBar authService={this.authService} isAuthenticated={this.isAuthenticated.bind(this)} />
        <BrowserRouter>
          <Switch>
            <Route exact path="/" component={Home} />
            <Route exact path="/hot" component={Hot} />
            <Route exact path="/trending" component={Trending} />
            <Route exact path="/upload" component={Upload} />
            <Route exact path="/video/:id" component={Detail} />
            <Route
              exact
              path="/auth/sign-up"
              render={(props) => <SignUp {...props} authService={this.authService} />}
            />
            <Route
              exact
              path="/auth/confirm"
              render={(props) => <Confirm {...props} authService={this.authService} />}
            />
            <Route
              exact
              path="/auth/log-in"
              render={(props) => (
                <LogIn {...props} authService={this.authService} setAuthenticated={this.setAuthenticated} />
              )}
            />
            <Route
              exact
              path="/auth/log-out"
              render={(props) => (
                <LogOut {...props} authService={this.authService} setAuthenticated={this.setAuthenticated} />
              )}
            />
          </Switch>
        </BrowserRouter>
      </>
    );
  }
}
