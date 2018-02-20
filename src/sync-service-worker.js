import { syncUserMediations } from './utils/sync'

self.addEventListener('sync', function (event) {
  if (event.tag === 'user_mediations') {
    event.waitUntil(syncUserMediations())
  }
})
