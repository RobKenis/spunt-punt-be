import React, { Component } from "react";
import { getAllVideos } from "../../api/VideoAdminClient";

const sortByDate = (a, b) => new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime();

export class Videos extends Component {
  state = {
    videos: [],
  };

  constructor(props, context) {
    super(props, context);
    getAllVideos().then((videos) => {
      this.setState({
        videos: videos,
      });
    });
  }

  render() {
    return (
      <table style={{ width: "100%" }}>
        <thead>
          <tr>
            <th>Title</th>
            <th>State</th>
            <th>Modified</th>
          </tr>
        </thead>
        <tbody>
          {this.state.videos
            .sort((v1, v2) => sortByDate(v1, v2))
            .map((video, index) => (
              <tr key={index}>
                <td>
                  <a href={`/video/${video.videoId}`}>{video.title}</a>
                </td>
                <td>{video.videoState}</td>
                <td>{video.lastModified}</td>
              </tr>
            ))}
        </tbody>
      </table>
    );
  }
}
