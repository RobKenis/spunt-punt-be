import React, { Component } from "react";
import "./VideoPreview.scss";

export class VideoPreview extends Component {
  render() {
    return (
      <div className="video-preview">
        <a href={`/video/${this.props.video.id}`}>
          <img src="https://placekitten.com/720/405" alt={this.props.video.title} />
          <h3>{this.props.video.title}</h3>
        </a>
      </div>
    );
  }
}
