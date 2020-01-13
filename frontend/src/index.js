import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Switch, Route } from "react-router-dom";

import { Home } from "./pages/overview/Home";
import { Hot } from "./pages/overview/Hot";
import { Trending } from "./pages/overview/Trending";
import { Upload } from "./pages/upload/Upload";
import { Detail } from "./pages/detail/Detail";
import { SignUp } from "./pages/auth/SignUp";
import { LogIn } from "./pages/auth/LogIn";
import { NavBar } from "./components/navbar/NavBar";

import "./index.scss";

ReactDOM.render(
  <BrowserRouter>
    <NavBar />
    <Switch>
      <Route exact path="/" component={Home} />
      <Route exact path="/hot" component={Hot} />
      <Route exact path="/trending" component={Trending} />
      <Route exact path="/upload" component={Upload} />
      <Route exact path="/video/:id" component={Detail} />
      <Route exact path="/sign-up" component={SignUp} />
      <Route exact path="/log-in" component={LogIn} />
    </Switch>
  </BrowserRouter>,
  document.querySelector("#root"),
);
