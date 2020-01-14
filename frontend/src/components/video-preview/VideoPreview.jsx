import React, { Component } from "react";
import "./VideoPreview.scss";

export const LAYOUT = {
  HORIZONTAL: "Horizontal",
  VERTICAL: "Vertical",
};

export class VideoPreview extends Component {
  render() {
    return (
      <div className={`video-preview video-preview--${this.props.layout.toLowerCase()}`}>
        <div className="video-preview__aspect-ratio--outer">
          <div className="video-preview__placeholder">
            S<span>.</span>
          </div>
          <a className="video-preview__aspect-ratio--inner" href={`/video/${this.props.video.videoId}`}>
            <img src={this.props.video.thumbnailUrl} alt={this.props.video.title} />
          </a>
        </div>
        <div className="video-preview__meta">
          <h3 className="video-preview__title">
            <a href={`/video/${this.props.video.videoId}`}>{this.props.video.title}</a>
          </h3>
        </div>
      </div>
    );
  }
}
