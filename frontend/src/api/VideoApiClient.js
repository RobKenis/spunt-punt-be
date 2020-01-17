import axios from "axios";

const api = axios.create({
  baseURL: "https://api.spunt.be/",
});

const getVideosOfType = async (type, limit) => {
  const response = await api.get(`/videos/${type}`);
  return response.data.videos.slice(0, limit);
};

export const getAllVideos = async (limit) => {
  return getVideosOfType("all", limit);
};

export const getHotVideos = async (limit) => {
  return getVideosOfType("hot", limit);
};

export const getTrendingVideos = async (limit) => {
  return getVideosOfType("trending", limit);
};

export const getRecommendedVideos = async (limit) => {
  return getVideosOfType("recommendations", limit);
};

export const getVideo = async (id) => {
  const response = await api.get("/video/" + id);
  return response.data;
};

const getPreSignedS3Data = async ({ title, file }) => {
  return await api.post("/v1/upload", {
    title: title,
    filename: file.name,
  });
};

const getFormData = ({ fields, file }) => {
  const formData = new FormData();
  formData.append("acl", fields["acl"]);
  formData.append("key", fields["key"]);
  formData.append("AWSAccessKeyId", fields["AWSAccessKeyId"]);
  formData.append("x-amz-security-token", fields["x-amz-security-token"]);
  formData.append("policy", fields["policy"]);
  formData.append("signature", fields["signature"]);
  formData.append("file", file);
  return formData;
};

export const uploadVideo = async ({ title, file }) => {
  try {
    const preSignedS3Data = await getPreSignedS3Data({ title, file });
    const s3url = preSignedS3Data.data.upload.url;
    const fields = preSignedS3Data.data.upload.fields;
    const formData = getFormData({ fields, file });
    await axios.post(s3url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return Promise.resolve(preSignedS3Data.data.videoId);
  } catch (e) {
    return Promise.reject(e);
  }
};

export const upvoteVideo = async ({ videoId, userId }) => {
  return await api.post("/v1/upvote", {
    videoId: videoId,
    userId: userId,
  });
};

export const downvoteVideo = async ({ videoId, userId }) => {
  return await api.post("/v1/downvote", {
    videoId: videoId,
    userId: userId,
  });
};
