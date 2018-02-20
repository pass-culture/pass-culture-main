export default async function registerSyncServiceWorker() {
  if ('serviceWorker' in navigator) {
    const swUrl = `${process.env.PUBLIC_URL}/sync-service-worker.js`
    const registration = await navigator.serviceWorker.register(swUrl)
    if (!navigator.serviceWorker.ready) {
      return
    }
    const userMediations = registration.sync.register('user_mediations')
  } else {
      //TODO: fetch user_mediations with a XMLHTTPRequest
  }
}
