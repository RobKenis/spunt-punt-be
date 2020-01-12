import React, { Component } from "react";
import { LAYOUT, VideoPreview } from "../video-preview/VideoPreview";
import "./VideoList.scss";

export class VideoList extends Component {
  render() {
    return (
      <div className="video-list">
        {this.props.videos.map((video, index) => (
          // TODO: Show items horizontally when we have more information (eg. title)
          <VideoPreview key={index} video={video} layout={LAYOUT.HORIZONTAL} />
        ))}
      </div>
    );
  }
}
