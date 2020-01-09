import React, { Component } from "react";
import { VideoPreview } from "../video-preview/VideoPreview";
import "./Video.scss";

export class Video extends Component {
  render() {
    return (
      <>
        <div
          className="theoplayer-container video-js theoplayer-skin"
          data-thumbnail-url={this.props.asset.thumbnailUrl}
          data-playback-url={this.props.asset.playbackUrl}
        />
      </>
    );
  }
}
