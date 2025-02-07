importScripts('https://cdn.by.wonderpush.com/sdk/1.1/wonderpush-loader.min.js');
WonderPush.init({
  webKey: (location.search.match(/[?&]webKey=([^&]*)/) || [])[1],
});
