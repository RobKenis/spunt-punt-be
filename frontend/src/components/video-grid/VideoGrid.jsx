import React, { Component } from "react";
import { VideoPreview } from "../video-preview/VideoPreview";
import "./VideoGrid.scss";

export class VideoGrid extends Component {
  render() {
    return (
      <>
        <h1 className="title">Home</h1>
        <div className="video-grid">
          {this.props.videos.map((video, index) => (
            <VideoPreview key={index} video={video} />
          ))}
        </div>
      </>
    );
  }
}
