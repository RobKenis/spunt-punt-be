const glob = require("glob");
const gulp = require("gulp");
const cssnano = require("gulp-cssnano");
const mediaQueriesSplitter = require("gulp-media-queries-splitter");

const files = glob.sync("dist/*.css", {});
const file = files[0];
const hash = file.split(".")[1];

gulp
  .src(file)
  .pipe(
    mediaQueriesSplitter([
      { media: ["none", { minUntil: "768px" }], filename: `mobile.${hash}.css` },
      { media: ["none", { min: "769px" }], filename: `tablet.${hash}.css` },
      { media: ["none", { min: "1024px" }], filename: `desktop.${hash}.css` },
    ]),
  )
  .pipe(cssnano())
  .pipe(gulp.dest("./dist"));
