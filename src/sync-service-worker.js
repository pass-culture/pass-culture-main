import { sync } from './utils/dexie'

self.addEventListener('sync', function (event) {
  if (event.tag === 'sync') {
    event.waitUntil(sync)
  }
})
