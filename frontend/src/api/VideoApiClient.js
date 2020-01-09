import axios from "axios";

const api = axios.create({
  baseURL: "https://api.spunt.be/",
});

export const getAllVideos = () => {
  return api.get("/videos/all");
};

export const getHotVideos = () => {
  return api.get("/videos/hot");
};

export const getTrendingVideos = () => {
  return api.get("/videos/trending");
};

export const getRecommendedVideos = () => {
  return api.get("/videos/recommendations");
};

export const getVideo = (id) => {
  return api.get("/video/" + id);
};
