#!/usr/bin/env bash

WORKING_DIRECTORY=$(pwd)
echo $WORKING_DIRECTORY

cd resources/custom_resources_code/elastictranscoder/
yarn install
zip -q -r elastictranscoder.zip index.js node_modules/
mv elastictranscoder.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building elastictranscoder.zip"
cd $WORKING_DIRECTORY

cd resources/video_encoding_engine/start_encode/
zip -q -r start_encode.zip index.py
mv start_encode.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building start_encode.zip"
cd $WORKING_DIRECTORY

cd resources/video_encoding_engine/request_encoding/
zip -q -r request_encoding.zip index.py
mv request_encoding.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building request_encoding.zip"
cd $WORKING_DIRECTORY

cd resources/video_encoding_engine/update_encoding_state/
zip -q -r update_encoding_state.zip index.py
mv update_encoding_state.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building update_encoding_state.zip"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/rekognition/
zip -q -r rekognition.zip index.py
mv rekognition.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building rekognition.zip"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/video_metadata_event/
zip -q -r video_metadata_event.zip index.py
mv video_metadata_event.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building video_metadata_event.zip"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/rekognition_results/
zip -q -r rekognition_results.zip index.py
mv rekognition_results.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building rekognition_results.zip"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/start_insights/
zip -q -r start_insights.zip index.py
mv start_insights.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building start_insights.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/all_videos/
zip -q -r all_videos.zip index.js
mv all_videos.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building all_videos.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/trending_videos/
zip -q -r trending_videos.zip index.js
mv trending_videos.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building trending_videos.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/hot_videos/
zip -q -r hot_videos.zip index.js
mv hot_videos.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building hot_videos.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/recommended_videos/
zip -q -r recommended_videos.zip index.js
mv recommended_videos.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building recommended_videos.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/rewrite_downvote/
zip -q -r rewrite_downvote.zip index.js
mv rewrite_downvote.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building rewrite_downvote.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/get_video/
zip -q -r get_video.zip index.js
mv get_video.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building get_video.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/consume_events/
zip -q -r consume_events.zip index.py
mv consume_events.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building consume_events.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/upvote/
zip -q -r upvote.zip index.py
mv upvote.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building upvote.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/upload/
zip -q -r upload.zip index.py
mv upload.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building upload.zip"
cd $WORKING_DIRECTORY

cd resources/spunt_api/rewrite_assets/
zip -q -r rewrite_assets.zip index.js
mv rewrite_assets.zip "$WORKING_DIRECTORY/output/"
echo " -> Finished building rewrite_assets.zip"
cd $WORKING_DIRECTORY
