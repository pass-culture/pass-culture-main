import { db, pushPull, setUser } from './utils/dexie'

const state = {}
let initPort = null

async function dexieUser (port) {
  // pull
  state.user && await setUser(state)
  // post
  port && port.postMessage({ text: "Hey I just set your user!" })
}

async function dexiePushPull (port) {
  // pull
  state.user && await pushPull(state)
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
    // update
    event.data.state &&
      Object.keys(event.data.state).length > 0 &&
      Object.assign(state, event.data.state)
    console.log('qsdsqdqdsd', key, state)
    // switch
    if (key === 'dexie-init') {
      initPort = event.ports[0]
      self.registration.sync.register(key)
    } else if (key === 'dexie-push-pull') {
      event.waitUntil(dexiePushPull(event.ports[0]))
    } else if (key === 'dexie-stop') {
      initPort = null
      self.registration.unregister()
    } else if (key === 'dexie-user') {
      event.waitUntil(dexieUser(event.ports[0]))
    }
  }
})

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-init') {
    event.waitUntil(dexiePushPull(initPort))
  }
})
