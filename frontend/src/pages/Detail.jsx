import React, { Component } from "react";
import { getVideo } from "../api/VideoApiClient";
import { Video } from "../components/video/Video";

export class Detail extends Component {
  state = {
    video: {},
  };

  componentDidMount() {
    getVideo(this.props.match.params.id).then((response) => {
      this.setState({
        video: response.data,
      });
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">{this.state.video.title}</h1>
        <Video asset={this.state.video} />
      </section>
    );
  }
}
