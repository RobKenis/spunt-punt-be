import React, { Component } from "react";
import { getTrendingVideos } from "../api/VideoApiClient";
import { VideoGrid } from "../components/video-grid/VideoGrid";

export class Trending extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getTrendingVideos().then((response) => {
      this.setState({
        videos: response.data.videos,
      });
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">Trending</h1>
        <VideoGrid videos={this.state.videos} />
      </section>
    );
  }
}
