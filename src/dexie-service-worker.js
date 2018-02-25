import { pull } from './utils/dexie'

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-pull') {
    event.waitUntil(pull)
  }
})
