const swUrl = `${process.env.PUBLIC_URL}/sync-service-worker.js`

export default async function registerSyncServiceWorker() {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register(swUrl)
    if (!navigator.serviceWorker.ready) {
      return
    }
    registration.sync.register('user_mediations')
  }
}
