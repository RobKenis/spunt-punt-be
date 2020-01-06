import React, { Component } from "react";
import { getRecentVideos } from "../../api/VideoApiClient";
import { VideoGrid } from "../../components/video-grid/VideoGrid";

export class Home extends Component {
  constructor(props, context) {
    super(props, context);
    this.videos = getRecentVideos();
  }

  render() {
    return (
      <section className="container section">
        <VideoGrid videos={this.videos} />
      </section>
    );
  }
}
