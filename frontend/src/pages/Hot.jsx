import React, { Component } from "react";
import { getHotVideos } from "../api/VideoApiClient";
import { VideoGrid } from "../components/video-grid/VideoGrid";

export class Hot extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getHotVideos().then((response) => {
      this.setState({
        videos: response.data.videos,
      });
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">Hot</h1>
        <VideoGrid videos={this.state.videos} />
      </section>
    );
  }
}
