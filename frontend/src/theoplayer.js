const urls = {
  library: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c",
  css: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/ui.css",
  js: "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/THEOplayer.js",
};

const initPlayer = (element) => {
  const player = new THEOplayer.Player(element, {
    libraryLocation: urls.library,
    ui: {
      fluid: true,
    },
  });

  player.source = {
    poster: element.dataset.thumbnailUrl,
    sources: [
      {
        src: element.dataset.playbackUrl,
        type: "application/dash+xml",
      },
    ],
  };
};

const init = (element) => {
  if (!element) return;

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = urls.css;
  document.head.appendChild(link);

  const script = document.createElement("script");
  script.src = urls.js;
  script.onload = initPlayer.bind(this, element);
  document.body.appendChild(script);
};

init(document.querySelector(".theoplayer-container"));
