import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload } from "@fortawesome/free-solid-svg-icons";
import { uploadVideo } from "../../api/VideoApiClient";
import "./Upload.scss";

export class Upload extends Component {
  state = {
    title: "",
    file: {},
  };

  handleTitleChange(e) {
    this.setState({ title: e.target.value });
  }

  handleFileChange(e) {
    this.setState({ file: e.target.files[0] });
  }

  handleSubmit(e) {
    e.preventDefault();
    uploadVideo(this.state.title, this.state.file.name).then((response) => {
      console.log(response);
    });
  }

  render() {
    return (
      <section className="container container--small section">
        <h1 className="title">Upload video</h1>
        <form onSubmit={this.handleSubmit.bind(this)}>
          <div className="field">
            <div className="control">
              <input
                className="input"
                type="text"
                name="title"
                placeholder="Title"
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
              <span className="file-name">{this.state.file.name || "Choose a file"}</span>
            </label>
          </div>
          <div className="field">
            <div className="control">
              <button className="button is-link">Submit</button>
            </div>
          </div>
        </form>
      </section>
    );
  }
}
