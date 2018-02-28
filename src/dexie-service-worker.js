import { db, pull } from './utils/dexie'

const store = {}
let port = null

async function dexiePull () {
  // pull
  await pull()
  // post
  console.log('port', port)
  port.postMessage({ text: "Hey I just got a fetch from you!" })
}

self.addEventListener('message', event => {
  const { key, type } = event.data
  if (type === 'sync') {
    if (!key) {
      console.warn('you need to define a key in event.data')
      return
    }
    console.log('key', key)
    if (key === 'dexie-init') {
      port = event.ports[0]
      self.registration.sync.register(key)
    }
    console.log('event.data.store', event.data.store)
    Object.keys(event.data.store).length > 0 && Object.assign(store, event.data.store)
  }
})

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-init') {
    console.log('store', store)
    event.waitUntil(dexiePull())
  }
})
