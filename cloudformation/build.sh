#!/usr/bin/env bash

WORKING_DIRECTORY=$(pwd)
echo $WORKING_DIRECTORY

cd resources/video_encoding_engine/start_encode/
zip -r start_encode.zip index.py
mv start_encode.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_encoding_engine/request_encoding/
zip -r request_encoding.zip index.py
mv request_encoding.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_encoding_engine/update_encoding_state/
zip -r update_encoding_state.zip index.py
mv update_encoding_state.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/rekognition/
zip -r rekognition.zip index.py
mv rekognition.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/video_metadata_event/
zip -r video_metadata_event.zip index.py
mv video_metadata_event.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/rekognition_results/
zip -r rekognition_results.zip index.py
mv rekognition_results.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/video_insights_engine/start_insights/
zip -r start_insights.zip index.py
mv start_insights.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/custom_resources_code/elastictranscoder/
yarn install
zip -r elastictranscoder.zip index.js node_modules/
mv elastictranscoder.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/all_videos/
zip -r all_videos.zip index.js
mv all_videos.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/trending_videos/
zip -r trending_videos.zip index.js
mv trending_videos.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/hot_videos/
zip -r hot_videos.zip index.js
mv hot_videos.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/recommended_videos/
zip -r recommended_videos.zip index.js
mv recommended_videos.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/rewrite_downvote/
zip -r rewrite_downvote.zip index.js
mv rewrite_downvote.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/get_video/
zip -r get_video.zip index.js
mv get_video.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/consume_events/
zip -r consume_events.zip index.py
mv consume_events.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/upvote/
zip -r upvote.zip index.py
mv upvote.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_api/upload/
zip -r upload.zip index.py
mv upload.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_auth/create_auth_challenge/
zip -r create_auth_challenge.zip index.js
mv create_auth_challenge.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_auth/verify_auth_challenge_response/
zip -r verify_auth_challenge_response.zip index.js
mv verify_auth_challenge_response.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_auth/pre_sign_up/
zip -r pre_sign_up.zip index.js
mv pre_sign_up.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_auth/post_authentication/
zip -r post_authentication.zip index.js
mv post_authentication.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY

cd resources/spunt_auth/define_auth_challenge/
zip -r define_auth_challenge.zip index.js
mv define_auth_challenge.zip "$WORKING_DIRECTORY/output/"
cd $WORKING_DIRECTORY
