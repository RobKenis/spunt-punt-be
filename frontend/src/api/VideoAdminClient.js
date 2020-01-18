import axios from "axios";

const api = axios.create({
  baseURL: "https://admin.spunt.be/",
});

export const getAllVideos = async () => {
  const response = await api.get(`/videos`);
  return response.data.videos;
};
