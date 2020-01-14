import React, { Component } from "react";
import { upvoteVideo } from "../../api/VideoApiClient";

export class UpvoteButton extends Component {
  constructor(props, context) {
    super(props, context);
  }

  upvote = () => upvoteVideo(this.props.videoId);

  render() {
    return <button onClick={() => this.upvote()}>Upvote</button>;
  }
}
