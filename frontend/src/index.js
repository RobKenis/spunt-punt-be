import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { Home } from "./pages/Home";
import { Hot } from "./pages/Hot";
import { Trending } from "./pages/Trending";
import { Detail } from "./pages/Detail";
import { SignUp } from "./pages/SignUp";
import { LogIn } from "./pages/LogIn";
import { NavBar } from "./components/navbar/NavBar";

import "./index.scss";

ReactDOM.render(
  <BrowserRouter>
    <NavBar />
    <Switch>
      <Route exact path="/" component={Home} />
      <Route exact path="/hot" component={Hot} />
      <Route exact path="/trending" component={Trending} />
      <Route exact path="/video/:id" component={Detail} />
      <Route exact path="/sign-up" component={SignUp} />
      <Route exact path="/log-in" component={LogIn} />
    </Switch>
  </BrowserRouter>,
  document.querySelector("#root"),
);
