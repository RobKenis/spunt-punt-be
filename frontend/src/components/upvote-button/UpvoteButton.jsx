import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUp } from "@fortawesome/free-solid-svg-icons";
import { AuthService } from "../../services/AuthService";
import { upvoteVideo } from "../../api/VideoApiClient";

export class UpvoteButton extends Component {
  authService;

  constructor(props, context) {
    super(props, context);
    this.authService = new AuthService();
  }

  upvote() {
    this.authService.isAuthenticated().then((isAuthenticated) => {
      if (isAuthenticated) {
        this.authService.getUserDetails().then((userDetails) => {
          const userId = userDetails.find((userDetail) => userDetail.Name === "sub").Value;
          upvoteVideo({ videoId: this.props.videoId, userId: userId }).then(() => {
            this.props.showVoteMessage("That's very kind of you!", false);
          });
        });
      } else {
        this.props.showVoteMessage("This only works when you're logged in.", true);
      }
    });
  }

  render() {
    return (
      <button className="button is-success" onClick={this.upvote.bind(this)}>
        <FontAwesomeIcon icon={faArrowUp} size="sm" fixedWidth />
      </button>
    );
  }
}
