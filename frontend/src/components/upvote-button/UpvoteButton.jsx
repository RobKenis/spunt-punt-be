import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUp } from "@fortawesome/free-solid-svg-icons";
import { downvoteVideo } from "../../api/VideoApiClient";

export class UpvoteButton extends Component {
  constructor(props, context) {
    super(props, context);
  }

  downvote() {
    downvoteVideo(this.props.videoId).then((response) => console.log(response));
  }

  render() {
    return (
      <button className="button is-success" onClick={this.downvote.bind(this)}>
        <FontAwesomeIcon icon={faArrowUp} size="sm" fixedWidth />
      </button>
    );
  }
}
