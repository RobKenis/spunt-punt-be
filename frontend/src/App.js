import React, { Component } from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { AuthService } from "./services/AuthService";
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
import { Videos } from "./pages/admin/Videos";

export class App extends Component {
  authService;

  state = {
    isAuthenticated: false,
  };

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
    this.isAuthenticated = this.isAuthenticated.bind(this);
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
        <NavBar isAuthenticated={this.isAuthenticated} />
        <BrowserRouter>
          <Switch>
            <Route exact path="/" component={Home} />
            <Route exact path="/hot" component={Hot} />
            <Route exact path="/trending" component={Trending} />
            <Route exact path="/upload" component={Upload} />
            <Route exact path="/video/:id" component={Detail} />
            <Route exact path="/auth/sign-up" component={SignUp} />
            <Route exact path="/auth/confirm" component={Confirm} />
            <Route exact path="/admin/videos" component={Videos} />
            <Route
              exact
              path="/auth/log-in"
              render={(props) => <LogIn {...props} setAuthenticated={this.setAuthenticated} />}
            />
            <Route
              exact
              path="/auth/log-out"
              render={(props) => <LogOut {...props} setAuthenticated={this.setAuthenticated} />}
            />
          </Switch>
        </BrowserRouter>
      </>
    );
  }
}
