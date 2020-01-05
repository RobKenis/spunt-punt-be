const body = {
    videos: [{
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }, {
        id: '3e72bdc6-28e3-11ea-abb5-5a2040ddf892',
        title: 'Very pretty title',
        playbackUrl: 'https://videos.spunt.be/3e72bdc6-28e3-11ea-abb5-5a2040ddf892/3e72bdc6-28e3-11ea-abb5-5a2040ddf892.mpd',
    }]
};

exports.handler = (event, context, callback) => {
    const response = {
        status: '200',
        statusDescription: 'OK',
        body: JSON.stringify(body),
    };
    callback(null, response);
};
