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
