import React, { Component } from "react";
import { getHotVideos } from "../../api/VideoApiClient";
import { VideoGrid } from "../../components/video-grid/VideoGrid";

const AMOUNT_OF_VIDEOS_TO_DISPLAY = 8;

export class Hot extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getHotVideos(AMOUNT_OF_VIDEOS_TO_DISPLAY).then((videos) => {
      this.setState({
        videos: videos,
      });
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">Hot</h1>
        <VideoGrid videos={this.state.videos} amount={AMOUNT_OF_VIDEOS_TO_DISPLAY} />
      </section>
    );
  }
}
