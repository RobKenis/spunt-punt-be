import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowDown } from "@fortawesome/free-solid-svg-icons";
import { downvoteVideo } from "../../api/VideoApiClient";

export class DownvoteButton extends Component {
  constructor(props, context) {
    super(props, context);
  }

  downvote() {
    downvoteVideo(this.props.videoId).then((response) => console.log(response));
  }

  render() {
    return (
      <button className="button is-danger" onClick={this.downvote.bind(this)}>
        <FontAwesomeIcon icon={faArrowDown} size="sm" fixedWidth />
      </button>
    );
  }
}
