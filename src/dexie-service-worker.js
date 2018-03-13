import { db,
  getData,
  pushPull,
  setUser
} from './utils/dexie'

const state = { rememberToken: null,
  user: null
}
let initPort = null

async function dexiePushPull (port) {
  // pull
  // state.user && await pushPull(state)
  await pushPull(state)
  // post
  port && port.postMessage({ text: "Hey I just got a fetch from you!" })
}

async function dexieSignin (port) {
  // check
  const { rememberToken, user } = state
  if (!rememberToken || !user) {
    return
  }
  // get the matching user
  const users = await getData('users', { rememberToken })
  if (users.length === 0) {
    await pushPull(state)
  }
  // setUser to set for the first time or just sync
  state.user && await setUser(state)
  // post
  port && port.postMessage({ text: "Hey I just set your user!" })
}

async function dexieSignout (port) {
  // check
  const { rememberToken, user } = state
  // clear
  state.rememberToken = null
  state.user = null
  db.users.clear()
  // post
  port && port.postMessage({ text: "Hey I just set your user!" })
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
    // switch
    if (key === 'dexie-init') {
      initPort = event.ports[0]
      self.registration.sync.register(key)
    } else if (key === 'dexie-push-pull') {
      event.waitUntil(dexiePushPull(event.ports[0]))
    } else if (key === 'dexie-stop') {
      initPort = null
      self.registration.unregister()
    } else if (key === 'dexie-signin') {
      event.waitUntil(dexieSignin(event.ports[0]))
    } else if (key === 'dexie-signout') {
      event.waitUntil(dexieSignout(event.ports[0]))
    }
  }
})

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-init') {
    event.waitUntil(dexiePushPull(initPort))
  }
})
