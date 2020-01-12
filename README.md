# Spunt.be

## Video Engine
The video engine handles uploaded videos in the `upload-s3-bucket` and encodes these files to a supported format by the THEOplayer.
For this case, we've picked MPEG-DASH.
### The flow
1. The uploaded file in S3 triggeres a notification to SNS
2. SNS forwards the message to a lambda to start the encode. This lambda creates an event in the `video-events-table`. 
After the lambda has executed, the resulting body is sent to the success-destination.
3. The success destination (SNS in this case) triggers the `request-encoding-lambda`. This lambda creates a job at
the Elastic Transcoder Pipeline to encode the `mp4` to `mpd`.
4. Elastic Transcoder sends updates to an SNS topic, the `update-state-lambda` is subscribed to this topic. When an
event is consumed, the state from the SNS message is saved as an event in the `video-events-table`.
5. That's all, the video is now available to be played.
#### Supported events
- NEW_VIDEO_UPLOADED
- ENCODING_REQUESTED
- ENCODING_STARTED
- ENCODING_FAILED
- ENCODING_COMPLETED
- METADATA_FLOW_STARTED
- REKOGNITION_STARTED
- VIDEO_LABELS_COLLECTED
- VIDEO_UPVOTED
