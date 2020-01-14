import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpinner, faUpload } from "@fortawesome/free-solid-svg-icons";
import { uploadVideo } from "../../api/VideoApiClient";
import "./Upload.scss";

export class Upload extends Component {
  state = {
    title: "",
    file: {},
    isUploading: false,
    hasError: false,
  };

  handleTitleChange(e) {
    this.setState({ title: e.target.value });
  }

  handleFileChange(e) {
    this.setState({ file: e.target.files[0] });
  }

  handleSubmit(e) {
    this.setState({ isUploading: true });
    uploadVideo(this.state.title, this.state.file)
      .then((response) => {
        this.setState({
          title: "",
          file: {},
          isUploading: false,
          hasError: false,
        });
        console.log(response);
      })
      .catch((err) => {
        this.setState({
          isUploading: false,
          hasError: true,
        });
        console.error(err);
      });
    e.preventDefault();
  }

  render() {
    return (
      <section className="container container--small section">
        <h1 className="title">Upload video</h1>
        {this.state.hasError && (
          <p className="has-text-danger">Something went wrong while uploading your video. Please try again.</p>
        )}
        <form onSubmit={this.handleSubmit.bind(this)}>
          <div className="field">
            <div className="control">
              <input
                className="input is-light"
                type="text"
                name="title"
                placeholder="Title of video"
                onChange={this.handleTitleChange.bind(this)}
              />
            </div>
          </div>
          <div className="file is-light is-fullwidth has-name">
            <label className="file-label">
              <input className="file-input" type="file" name="file" onChange={this.handleFileChange.bind(this)} />
              <span className="file-cta">
                <span className="file-icon">
                  <FontAwesomeIcon icon={faUpload} size="sm" fixedWidth />
                </span>
              </span>
              <span className="file-name">{this.state.file.name || "Choose a video"}</span>
            </label>
          </div>
          <div className="field">
            <div className="control">
              <button className="button is-link" disabled={this.state.isUploading}>
                {this.state.isUploading && <FontAwesomeIcon icon={faSpinner} size="sm" fixedWidth spin />} Submit
              </button>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
