import React, { Component } from "react";
import "./Video.scss";
import { UpvoteButton } from "../upvote-button/UpvoteButton";
import { DownvoteButton } from "../downvote-button/DownvoteButton";

export class Video extends Component {
  render() {
    return (
      <div className="video">
        <div
          className="video__player theoplayer-container theoplayer-skin video-js"
          data-thumbnail-url={this.props.video.thumbnailUrl}
          data-playback-url={this.props.video.playbackUrl}
        />
        <div className="field is-grouped">
          <p className="control">
            <UpvoteButton videoId={this.props.video.videoId} />
          </p>
          <p className="control">
            <DownvoteButton videoId={this.props.video.videoId} />
          </p>
        </div>
        <ul className="video__labels">
          {this.props.video.labels &&
            this.props.video.labels.slice(0, 3).map((label, index) => (
              <li key={index} className="video__label">
                {label}
              </li>
            ))}
        </ul>
      </div>
    );
  }
}
