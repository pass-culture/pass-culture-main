import { db, pull } from './utils/dexie'

const store = {}
let initPort = null

async function dexiePull (port) {
  // pull
  await pull(store)
  // post
  port && port.postMessage({ text: "Hey I just got a fetch from you!" })
}

self.addEventListener('message', event => {
  const { key, type } = event.data
  if (type === 'sync') {
    // check
    if (!key) {
      console.warn('you need to define a key in event.data')
      return
    }
    // switch
    if (key === 'dexie-init') {
      initPort = event.ports[0]
      self.registration.sync.register(key)
    } else if (key === 'dexie-pull') {
      event.waitUntil(dexiePull(event.ports[0]))
    } else if (key === 'dexie-stop') {
      initPort = null
      self.registration.unregister()
    }
    // update
    event.data.store &&
      Object.keys(event.data.store).length > 0 &&
      Object.assign(store, event.data.store)
  }
})

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-init') {
    event.waitUntil(dexiePull(initPort))
  }
})
