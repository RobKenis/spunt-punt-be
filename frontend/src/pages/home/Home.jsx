import React, { Component } from "react";
import { getAllVideos } from "../../api/VideoApiClient";
import { VideoGrid } from "../../components/video-grid/VideoGrid";

export class Home extends Component {
  state = {
    videos: [],
  };

  componentDidMount() {
    getAllVideos().then((response) => {
      this.setState({
        videos: response.data.videos,
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
