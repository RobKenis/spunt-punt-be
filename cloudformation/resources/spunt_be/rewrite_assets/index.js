"use strict";

exports.handler = async (event) => {
  const request = event.Records[0].cf.request;

  const isMobileViewer = () => {
    return request.headers["cloudfront-is-mobile-viewer"]
      && request.headers["cloudfront-is-mobile-viewer"][0].value === "true"
  };

  const isTabletViewer = () => {
    return request.headers["cloudfront-is-tablet-viewer"]
      && request.headers["cloudfront-is-tablet-viewer"][0].value === "true"
  };

  const isDesktopViewer = () => {
    return request.headers["cloudfront-is-desktop-viewer"]
      && request.headers["cloudfront-is-desktop-viewer"][0].value === "true"
  };

  if (isMobileViewer()) {
    request.uri = request.uri.replace(new RegExp("(\/)?src\.(.*)\.css", "gm"), "$1mobile.$2.css");
  } else if (isTabletViewer()) {
    request.uri = request.uri.replace(new RegExp("(\/)?src\.(.*)\.css", "gm"), "$1tablet.$2.css");
  } else if (isDesktopViewer()) {
    request.uri = request.uri.replace(new RegExp("(\/)?src\.(.*)\.css", "gm"), "$1desktop.$2.css");
  }

  return request;
};
