const CfnLambda = require('cfn-lambda');
const AWS = require('aws-sdk');

const elastictranscoder = new AWS.ElasticTranscoder();

function currentRegion(context) {
    return context.invokedFunctionArn.match(/^arn:aws:lambda:(\w+-\w+-\d+):/)[1];
}

exports.handler = function ElasticTranscoderPipelineHandler(event, context) {
    const ElasticTranscoderPipeline = CfnLambda({
        Create: function (params, reply) {
            elastictranscoder.createPipeline(params, function (err, data) {
                if (err) {
                    console.error(err);
                    reply(err);
                } else {
                    reply(null, data.Pipeline.Id, {"Arn": data.Pipeline.Arn});
                }
            });
        },
        Update: function (physicalId, params, oldParams, reply) {
            params.Id = physicalId;
            delete params.OutputBucket;
            elastictranscoder.updatePipeline(params, function (err, data) {
                if (err) {
                    console.error(err);
                    reply(err);
                } else {
                    reply(null, data.Pipeline.Id, {"Arn": data.Pipeline.Arn});
                }
            });
        },
        Delete: function (physicalId, params, reply) {
            const p = {
                Id: physicalId
            };
            elastictranscoder.deletePipeline(p, function (err, data) {
                if (err) console.error(err);
                reply(err, physicalId);
            });
        },
        Schema: {
            "type": "object",
            "required": [
                "Name",
                "Role",
                "InputBucket"
            ],
            "additionalProperties": false,
            "properties": {
                "Name": {
                    "type": "string"
                },
                "Role": {
                    "type": "string",
                    "pattern": "arn:aws:iam::[0-9]*:role\/[\\w-\\d]*"
                },
                "InputBucket": {
                    "type": "string"
                },
                "OutputBucket": {
                    "type": "string"
                },
                "AwsKmsKeyArn": {
                    "type": "string",
                    "pattern": "arn:aws:kms:(\\w+-\\w+-\\d+):[0-9]*:key\/[\\w-\\d]*"
                },
                "ContentConfig": {
                    "type": "object",
                    "required": [
                        "Bucket",
                        "StorageClass"
                    ],
                    "additionalProperties": false,
                    "properties": {
                        "Bucket": {
                            "type": "string"
                        },
                        "Permissions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "Access",
                                    "Grantee",
                                    "GranteeType"
                                ],
                                "additionalProperties": false,
                                "properties": {
                                    "Access": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": [
                                                "Read",
                                                "ReadAcp",
                                                "WriteAcp",
                                                "FullControl"
                                            ]
                                        }
                                    },
                                    "Grantee": {
                                        "type": "string"
                                    },
                                    "GranteeType": {
                                        "type": "string",
                                        "enum": [
                                            "Canonical",
                                            "Email",
                                            "Group"
                                        ]
                                    }
                                }
                            }
                        },
                        "StorageClass": {
                            "type": "string",
                            "enum": [
                                "Standard",
                                "ReducedRedundancy"
                            ]
                        }
                    }
                },
                "ThumbnailConfig": {
                    "type": "object",
                    "required": [
                        "Bucket",
                        "StorageClass"
                    ],
                    "additionalProperties": false,
                    "properties": {
                        "Bucket": {
                            "type": "string"
                        },
                        "Permissions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "Access",
                                    "Grantee",
                                    "GranteeType"
                                ],
                                "additionalProperties": false,
                                "properties": {
                                    "Access": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": [
                                                "Read",
                                                "ReadAcp",
                                                "WriteAcp",
                                                "FullControl"
                                            ]
                                        }
                                    },
                                    "Grantee": {
                                        "type": "string"
                                    },
                                    "GranteeType": {
                                        "type": "string",
                                        "enum": [
                                            "Canonical",
                                            "Email",
                                            "Group"
                                        ]
                                    }
                                }
                            }
                        },
                        "StorageClass": {
                            "type": "string",
                            "enum": [
                                "Standard",
                                "ReducedRedundancy"
                            ]
                        }
                    }
                },
                "Notifications": {
                    "type": "object",
                    "additionalProperties": false,
                    "properties": {
                        "Completed": {
                            "type": "string",
                            "pattern": "arn:aws:sns:(\\w+-\\w+-\\d+):[0-9]*:[\\w-]*"
                        },
                        "Error": {
                            "type": "string",
                            "pattern": "arn:aws:sns:(\\w+-\\w+-\\d+):[0-9]*:[\\w-]*"
                        },
                        "Progressing": {
                            "type": "string",
                            "pattern": "arn:aws:sns:(\\w+-\\w+-\\d+):[0-9]*:[\\w-]*"
                        },
                        "Warning": {
                            "type": "string",
                            "pattern": "arn:aws:sns:(\\w+-\\w+-\\d+):[0-9]*:[\\w-]*"
                        }
                    }
                }
            }
        }
    });
    AWS.config.region = currentRegion(context);

    return ElasticTranscoderPipeline(event, context);
};
