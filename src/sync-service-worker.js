import { syncUserMediations } from './utils/dexie'

self.addEventListener('sync', function (event) {
  if (event.tag === 'user_mediations') {
    event.waitUntil(syncUserMediations())
  }
})
