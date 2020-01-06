import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { Home } from "./pages/home/Home";
import { Hot } from "./pages/hot/Hot";
import { Trending } from "./pages/trending/Trending";
import { SignUp } from "./pages/sign-up/SignUp";
import { LogIn } from "./pages/log-in/LogIn";
import { NavBar } from "./components/navbar/NavBar";

import "./index.scss";

ReactDOM.render(
  <BrowserRouter>
    <NavBar />
    <Switch>
      <Route exact path="/" component={Home} />
      <Route exact path="/hot" component={Hot} />
      <Route exact path="/trending" component={Trending} />
      <Route exact path="/sign-up" component={SignUp} />
      <Route exact path="/log-in" component={LogIn} />
    </Switch>
  </BrowserRouter>,
  document.querySelector("#root"),
);
