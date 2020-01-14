import React from "react";
import { downvoteVideo } from "../../api/VideoApiClient";

export const DownvoteButton = ({ videoId }) => <button onClick={() => downvoteVideo(videoId)}>Downvote</button>;
