import React, { Component } from "react";
import "./VideoPreview.scss";

export class VideoPreview extends Component {
  render() {
    return (
      <div className="video-preview">
        <img src="https://placekitten.com/400/225" alt={this.props.video.title} />
        <h3>{this.props.video.title}</h3>
      </div>
    );
  }
}
