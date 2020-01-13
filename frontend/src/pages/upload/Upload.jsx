import React, { Component } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload } from "@fortawesome/free-solid-svg-icons";
import { uploadVideo } from "../../api/VideoApiClient";
import "./Upload.scss";

export class Upload extends Component {
  state = {
    file: {},
  };

  handleFileChange(e) {
    this.setState({ file: e.target.files[0] });
  }

  handleSubmit(e) {
    e.preventDefault();
    uploadVideo(this.state.file).then((response) => {
      console.log(response);
    });
  }

  render() {
    return (
      <section className="container section">
        <h1 className="title">Upload video</h1>
        <form onSubmit={this.handleSubmit.bind(this)}>
          <div className="file is-light is-fullwidth has-name">
            <label className="file-label">
              <input className="file-input" type="file" name="resume" onChange={this.handleFileChange.bind(this)} />
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
