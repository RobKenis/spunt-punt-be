# Theoplayer

Theoplayer is set up for 10k impressions per month.

## Current version
Library is at: https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c

## Example usage
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>THEOplayer 2.X: Getting Started</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <!-- THEOplayer CSS -->
        <link
            rel="stylesheet"
            type="text/css"
            href="https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/ui.css"
        />
    </head>
    <body>
        <div class="theoplayer-container video-js theoplayer-skin"></div>
        <!-- add THEOplayer library -->
        <script
            type="text/javascript"
            src="https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c/THEOplayer.js"
        ></script>
        <script>
            var element = document.querySelector(".theoplayer-container");
            var player = new THEOplayer.Player(element, {
                libraryLocation:
                    "https://cdn.myth.theoplayer.com/3fad4d9d-d17b-4934-8943-be34a3fe4d4c"
            });

            // How to use an HLS Stream
            player.source = {
                sources: [
                    {
                        src:
                            "https://cdn.theoplayer.com/video/elephants-dream/playlist-single-audio.m3u8",
                        type: "application/x-mpegurl"
                    }
                ]
            };
        </script>
    </body>
</html>

```