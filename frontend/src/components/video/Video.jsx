import React, { Component } from "react";
import { VideoPreview } from "../video-preview/VideoPreview";
import "./Video.scss";

export class Video extends Component {
  render() {
    return (
      <div className="video">
        <div
          className="video__player theoplayer-container theoplayer-skin video-js"
          data-thumbnail-url={this.props.video.thumbnailUrl}
          data-playback-url={this.props.video.playbackUrl}
        />
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
