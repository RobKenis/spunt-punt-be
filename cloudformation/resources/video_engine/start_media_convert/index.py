import boto3

client = boto3.client('mediaconvert', endpoint_url='https://lxlxpswfb.mediaconvert.us-east-1.amazonaws.com')

client.create_job(
    Queue='spunt-video-engine',
    Role='arn:aws:iam::840471932663:role/spunt-video-engine-MediaConvertRole-1DZNESXT7907Q',
    Settings={
        "AdAvailOffset": 0,
        "Inputs": [
            {
                "FilterEnable": "AUTO",
                "PsiControl": "USE_PSI",
                "FilterStrength": 0,
                "DeblockFilter": "DISABLED",
                "DenoiseFilter": "DISABLED",
                "TimecodeSource": "EMBEDDED",
                "VideoSelector": {
                    "ColorSpace": "FOLLOW",
                    "Rotate": "DEGREE_0",
                    "AlphaBehavior": "DISCARD"
                },
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "Offset": 0,
                        "DefaultSelection": "DEFAULT",
                        "ProgramSelection": 1
                    }
                },
                "FileInput": "s3://spunt-video-engine-upload/upload/bbb_sunflower_1080p_60fps_normal.mp4"
            }
        ],
        "OutputGroups": [
            {
                "Name": "DASH ISO",
                "OutputGroupSettings": {
                    "Type": "DASH_ISO_GROUP_SETTINGS",
                    "DashIsoGroupSettings": {
                        "SegmentLength": 30,
                        "FragmentLength": 2,
                        "SegmentControl": "SINGLE_FILE",
                        "MpdProfile": "MAIN_PROFILE",
                        "HbbtvCompliance": "NONE",
                        "Destination": "s3://spunt-video-engine-upload/output/"
                    }
                },
                "Outputs": [
                    {
                        "VideoDescription": {
                            "ScalingBehavior": "DEFAULT",
                            "TimecodeInsertion": "DISABLED",
                            "AntiAlias": "ENABLED",
                            "Sharpness": 50,
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "InterlaceMode": "PROGRESSIVE",
                                    "NumberReferenceFrames": 3,
                                    "Syntax": "DEFAULT",
                                    "Softness": 0,
                                    "GopClosedCadence": 1,
                                    "GopSize": 90,
                                    "Slices": 1,
                                    "GopBReference": "DISABLED",
                                    "SlowPal": "DISABLED",
                                    "SpatialAdaptiveQuantization": "ENABLED",
                                    "TemporalAdaptiveQuantization": "ENABLED",
                                    "FlickerAdaptiveQuantization": "DISABLED",
                                    "EntropyEncoding": "CABAC",
                                    "FramerateControl": "INITIALIZE_FROM_SOURCE",
                                    "RateControlMode": "CBR",
                                    "CodecProfile": "MAIN",
                                    "Telecine": "NONE",
                                    "MinIInterval": 0,
                                    "AdaptiveQuantization": "HIGH",
                                    "CodecLevel": "AUTO",
                                    "FieldEncoding": "PAFF",
                                    "SceneChangeDetect": "ENABLED",
                                    "QualityTuningLevel": "SINGLE_PASS",
                                    "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                                    "UnregisteredSeiTimecode": "DISABLED",
                                    "GopSizeUnits": "FRAMES",
                                    "ParControl": "INITIALIZE_FROM_SOURCE",
                                    "NumberBFramesBetweenReferenceFrames": 2,
                                    "RepeatPps": "DISABLED",
                                    "DynamicSubGop": "STATIC",
                                    "Bitrate": 1000
                                }
                            },
                            "AfdSignaling": "NONE",
                            "DropFrameTimecode": "ENABLED",
                            "RespondToAfd": "NONE",
                            "ColorMetadata": "INSERT"
                        },
                        "AudioDescriptions": [
                            {
                                "AudioTypeControl": "FOLLOW_INPUT",
                                "CodecSettings": {
                                    "Codec": "AAC",
                                    "AacSettings": {
                                        "AudioDescriptionBroadcasterMix": "NORMAL",
                                        "Bitrate": 96000,
                                        "RateControlMode": "CBR",
                                        "CodecProfile": "LC",
                                        "CodingMode": "CODING_MODE_2_0",
                                        "RawFormat": "NONE",
                                        "SampleRate": 48000,
                                        "Specification": "MPEG4"
                                    }
                                },
                                "LanguageCodeControl": "FOLLOW_INPUT"
                            }
                        ],
                        "ContainerSettings": {
                            "Container": "MPD"
                        }
                    }
                ],
                "CustomName": "MPD"
            }
        ]
    }
)
