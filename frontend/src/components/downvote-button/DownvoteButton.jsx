import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowDown } from "@fortawesome/free-solid-svg-icons";
import { AuthService } from "../../services/AuthService";
import { downvoteVideo } from "../../api/VideoApiClient";

export class DownvoteButton extends Component {
  authService;

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
  }

  downvote() {
    this.authService.isAuthenticated().then((isAuthenticated) => {
      if (isAuthenticated) {
        this.authService.getUserDetails().then((userDetails) => {
          const userId = userDetails.find((userDetail) => userDetail.Name === "sub").Value;
          downvoteVideo({ videoId: this.props.videoId, userId: userId }).then(() => {
            this.props.showVoteMessage("Why so serious?", false);
          });
        });
      } else {
        this.props.showVoteMessage("This only works when you're logged in.", true);
      }
    });
  }

  render() {
    return (
      <button className="button is-danger" onClick={this.downvote.bind(this)}>
        <FontAwesomeIcon icon={faArrowDown} size="sm" fixedWidth />
      </button>
    );
  }
}
