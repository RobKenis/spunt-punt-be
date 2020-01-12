import React, { Component } from "react";
import "./VideoPreview.scss";

export class VideoPreview extends Component {
  render() {
    return (
      <div className="video-preview">
        <div className="video-preview__aspect-ratio--outer">
          <div className="video-preview__placeholder">
            S<span>.</span>
          </div>
          <a className="video-preview__aspect-ratio--inner" href={`/video/${this.props.video.videoId}`}>
            <img src={this.props.video.thumbnailUrl} alt={this.props.video.title} />
          </a>
        </div>
        <h3>{this.props.video.title}</h3>
      </div>
    );
  }
}
