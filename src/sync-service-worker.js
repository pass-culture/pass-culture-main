import db from 'db'

self.addEventListener('sync', function (event) {
  if (event.tag === 'user_mediations') {
    event.waitUntil(syncUserMediations());
  }
})

function syncUserMediations () {
    fetch('./doge.png')
        .then(function (response) {
        return response;
        })
        .then(function (text) {
        console.log('Request successful', text);
        })
        .catch(function (error) {
        console.log('Request failed', error);
        });
    }
