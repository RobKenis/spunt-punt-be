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

export const uploadVideo = async (file) => {
  const formData = new FormData();
  /*
    ("acl", "bucket-owner-full-control");
    ("key", `upload/32cfdb06-3645-11ea-8cbd-4e467ef0029a/${file.name}`);
    ("AWSAccessKeyId", "ASIA4HMAH533RXTMBXF2");
    ("x-amz-security-token", "IQoJb3JpZ2luX2VjEMX//////////wEaCXVzLWVhc3QtMSJHMEUCIFxNki65bV84wYH5wNypIE93+BYdLpKHuG3PvjHUkZ/4AiEAgZnaFeA3+cv3I/luREHe8QtdA3Nduzg2jh/1vgm3m24q5AEIThABGgw4NDA0NzE5MzI2NjMiDKa1f2AsQ9QjEl0XaSrBAZ/pbTdazrU2UUQp7AqGC4O6kCSZTXYOgMPZe5Ws0ZXdaXendUsWQoFbXNhc8LGVk73sSZxe3kRpse+sYJCNBB1uSTHY/HWbUJYRwij8zv+7PrE/3KfIMuOoOPZUP/nhb+tUXVFgbEhDldJsKKnjhFFeN3ank+G4tVqbHNo63vjytGAkoqhLSA9FTqnwhSeDPVoVkiucaR+RNsph3SRGF/S8OxZOdT3W7oj7g05wajttx68XtBD9MWOk25oEU21oFEQwvKnz8AU64AGoeK7EhpIIp/T58DKXrZzy7XAdkUvgwGbEkno+aDULCqwgNIZy1np+IvyO6l7P4olHYFfXacSa9yBRHufNfFX3PUI8MqHGVlTizF7pnnCrCv2w7j2kcI4SwHgS+fvbRnejihJxJ16H16oYXa08FPRaQ4JDbeDeYX09mf8Du8V6Z8Qmh6BAYXlzlGyXmbIU3cKaCxnIGPR2y1934FGsMbqu7J6UgoOP8Lnz7WSWb61YmBPYR/Qn/UG1TcGLxHOrpJUoyohinecNWOf0ICgeZggiesZ2h9InV/vz0YFDTXsiTg==");
    ("policy", "eyJleHBpcmF0aW9uIjogIjIwMjAtMDEtMTNUMjE6NDI6MjJaIiwgImNvbmRpdGlvbnMiOiBbeyJhY2wiOiAiYnVja2V0LW93bmVyLWZ1bGwtY29udHJvbCJ9LCBbImNvbnRlbnQtbGVuZ3RoLXJhbmdlIiwgMSwgMzE0NTcyODAwXSwgeyJidWNrZXQiOiAic3B1bnQtdmlkZW8tZW5jb2RpbmctZW5naW5lLXVwbG9hZCJ9LCB7ImtleSI6ICJ1cGxvYWQvMzJjZmRiMDYtMzY0NS0xMWVhLThjYmQtNGU0NjdlZjAwMjlhL2luaWVzdGFfd2MubXA0In0sIHsieC1hbXotc2VjdXJpdHktdG9rZW4iOiAiSVFvSmIzSnBaMmx1WDJWakVNWC8vLy8vLy8vLy93RWFDWFZ6TFdWaGMzUXRNU0pITUVVQ0lGeE5raTY1YlY4NHdZSDV3TnlwSUU5MytCWWRMcEtIdUczUHZqSFVrWi80QWlFQWdabmFGZUEzK2N2M0kvbHVSRUhlOFF0ZEEzTmR1emcyamgvMXZnbTNtMjRxNUFFSVRoQUJHZ3c0TkRBME56RTVNekkyTmpNaURLYTFmMkFzUTlRakVsMFhhU3JCQVovcGJUZGF6clUyVVVRcDdBcUdDNE82a0NTWlRYWU9nTVBaZTVXczBaWGRhWGVuZFVzV1FvRmJYTmhjOExHVms3M3NTWnhlM2tScHNlK3NZSkNOQkIxdVNUSFkvSFdiVUpZUndpajh6dis3UHJFLzNLZklNdU9vT1BaVVAvbmhiK3RVWFZGZ2JFaERsZEpzS0tuamhGRmVOM2FuaytHNHRWcWJITm82M3ZqeXRHQWtvcWhMU0E5RlRxbndoU2VEUFZvVmtpdWNhUitSTnNwaDNTUkdGL1M4T3haT2RUM1c3b2o3ZzA1d2FqdHR4NjhYdEJEOU1XT2syNW9FVTIxb0ZFUXd2S256OEFVNjRBR29lSzdFaHBJSXAvVDU4REtYclp6eTdYQWRrVXZnd0diRWtubythRFVMQ3F3Z05JWnkxbnArSXZ5TzZsN1A0b2xIWUZmWGFjU2E5eUJSSHVmTmZGWDNQVUk4TXFIR1ZsVGl6Rjdwbm5DckN2Mnc3ajJrY0k0U3dIZ1MrZnZiUm5lamloSnhKMTZIMTZvWVhhMDhGUFJhUTRKRGJlRGVZWDA5bWY4RHU4VjZaOFFtaDZCQVlYbHpsR3lYbWJJVTNjS2FDeG5JR1BSMnkxOTM0RkdzTWJxdTdKNlVnb09QOExuejdXU1diNjFZbUJQWVIvUW4vVUcxVGNHTHhIT3JwSlVveW9oaW5lY05XT2YwSUNnZVpnZ2llc1oyaDlJblYvdnowWUZEVFhzaVRnPT0ifV19");
    ("signature", "Q87uzkLvAD6gQBthUzQyjWqRntw=");
  */
  formData.append("file", file);
  return await api.post("/v1/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};
