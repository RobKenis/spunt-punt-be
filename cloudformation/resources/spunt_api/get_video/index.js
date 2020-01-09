const body = {
  id: "3e72bdc6-28e3-11ea-abb5-5a2040ddf892",
  title: "Very pretty title",
  playbackUrl: "https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd",
  thumbnailUrl: "https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.jpg"
};

exports.handler = (event, context, callback) => {
  const response = {
    status: "200",
    statusDescription: "OK",
    body: JSON.stringify(body),
    headers: {
      "access-control-allow-origin": [
        { key: "Access-Control-Allow-Origin", value: "*" }
      ],
      "access-control-allow-methods": [
        { key: "Access-Control-Allow-Methods", value: "GET, HEAD, OPTIONS" }
      ],
      "access-control-max-age": [
        { key: "Access-Control-Max-Age", value: "86400" }
      ]
    }
  };
  callback(null, response);
};
