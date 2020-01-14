import React, { Component } from "react";
import { UpvoteButton } from "../upvote-button/UpvoteButton";
import { DownvoteButton } from "../downvote-button/DownvoteButton";
import "./Video.scss";

const urls = {
  library: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c",
  css: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/ui.css",
  js: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/THEOplayer.js",
};

const waitForGlobal = (key, callback) => {
  if (window[key]) {
    callback();
  } else {
    setTimeout(function() {
      waitForGlobal(key, callback);
    }, 50);
  }
};

export class Video extends Component {
  constructor(props, context) {
    super(props, context);
    this.initializePlayer = this.initializePlayer.bind(this);
  }

  componentDidMount() {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = urls.css;
    document.head.appendChild(link);

    const script = document.createElement("script");
    script.src = urls.js;
    document.body.appendChild(script);

    this.initializePlayer(this.props.video);
  }

  componentDidUpdate(prevProps) {
    if (this.props.video !== prevProps.video) {
      this.initializePlayer(this.props.video);
    }
  }

  initializePlayer(props) {
    if (!props.thumbnailUrl || !props.playbackUrl) {
      return;
    }

    waitForGlobal("THEOplayer", () => {
      const player = new THEOplayer.Player(this.refs.video, {
        libraryLocation: urls.library,
        ui: {
          fluid: true,
        },
      });

      player.source = {
        poster: props.thumbnailUrl,
        sources: [
          {
            src: props.playbackUrl,
            type: "application/dash+xml",
          },
        ],
      };
    });
  }

  render() {
    return (
      <div className="video">
        <div className="video__aspect-ratio--outer">
          <div className="video-preview__placeholder">
            S<span>.</span>
          </div>
          <div className="video__aspect-ratio--inner">
            <div className="video__player theoplayer-container theoplayer-skin video-js" ref="video" />
          </div>
        </div>
        <div className="video__meta">
          <div className="field is-grouped">
            <p className="control">
              <UpvoteButton videoId={this.props.video.videoId} />
            </p>
            <p className="control">
              <DownvoteButton videoId={this.props.video.videoId} />
            </p>
          </div>
          <ul className="video__labels">
            {this.props.video.labels &&
              this.props.video.labels.map((label, index) => (
                <li key={index} className="video__label button is-white is-outlined">
                  {label}
                </li>
              ))}
          </ul>
        </div>
      </div>
    );
  }
}
