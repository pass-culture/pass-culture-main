export default function registerSyncServiceWorker() {
    if ('serviceWorker' in navigator) {
        const swUrl = `${process.env.PUBLIC_URL}/sync-service-worker.js`;
        navigator.serviceWorker.register(swUrl)
               .then(registration => navigator.serviceWorker.ready)
               .then(registration => {
                   registration.sync.register('user_mediations').then(() => {
                       console.log('Sync registered');
                       });
                   });
    } else {
        //TODO: fetch user_mediations with a XMLHTTPRequest
    }
}
