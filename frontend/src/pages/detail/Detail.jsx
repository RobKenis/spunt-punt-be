import React, { Component } from "react";
import { getHotVideos, getVideo } from "../../api/VideoApiClient";
import { VideoList } from "../../components/video-list/VideoList";
import { Video } from "../../components/video/Video";
import "./Detail.scss";

export class Detail extends Component {
  state = {
    video: {},
    related: [],
  };

  constructor(props, context) {
    super(props, context);
    getVideo(this.props.match.params.id).then((video) => {
      this.setState({
        video: video,
      });
    });
    getHotVideos(8).then((videos) => {
      this.setState({
        related: videos,
      });
    });
  }

  render() {
    return (
      <section className="container section detail">
        <Video video={this.state.video} />
        <VideoList videos={this.state.related} />
      </section>
    );
  }
}
