import React, { Component } from "react";
import { getAllVideos } from "../../api/VideoApiClient";
import { VideoGrid } from "../../components/video-grid/VideoGrid";

const AMOUNT_OF_VIDEOS_TO_DISPLAY = 16;

export class Home extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getAllVideos(AMOUNT_OF_VIDEOS_TO_DISPLAY).then((videos) => {
      this.setState({
        videos: videos,
      });
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">Home</h1>
        <VideoGrid videos={this.state.videos} />
      </section>
    );
  }
}
