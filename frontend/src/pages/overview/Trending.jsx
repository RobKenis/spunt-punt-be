import React, { Component } from "react";
import { getTrendingVideos } from "../../api/VideoApiClient";
import { VideoGrid } from "../../components/video-grid/VideoGrid";

const AMOUNT_OF_VIDEOS_TO_DISPLAY = 8;

export class Trending extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getTrendingVideos(AMOUNT_OF_VIDEOS_TO_DISPLAY).then((videos) => {
      this.setState({
        videos: videos,
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
