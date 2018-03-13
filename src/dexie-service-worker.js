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
  port && port.postMessage({ isSyncRedux: true,
    text: "dexiePushPull"
  })
}

async function dexieSignin (port) {
  // check
  const { rememberToken, user } = state
  if (!rememberToken || !user) {
    return
  }
  // get the matching user
  const users = await getData('users', { rememberToken })
  console.log('users', users)
  if (users.length === 0 || user.rememberToken !== state.user.rememberToken) {
    // trigger a first push pull to feed the dexie
    await dexiePushPull(port)
  } else {
    // if the user is already here we need just to trigger a
    // sync of the redux state
    port && port.postMessage({ isSyncRedux: true })
  }
  // setUser to set for the first time or just sync
  state.user && await setUser(state)
  // post
  port && port.postMessage({ text: "dexieSignin" })
}

async function dexieSignout (port) {
  // check
  const { rememberToken, user } = state
  // clear
  state.rememberToken = null
  state.user = null
  db.users.clear()
  // post
  port && port.postMessage({ text: "dexieSignout" })
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
