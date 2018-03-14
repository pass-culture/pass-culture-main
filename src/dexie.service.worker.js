import { db,
  getData,
  pushPull,
  setUser
} from './utils/dexie'

const state = {}

async function dexiePushPull () {
  // pull
  state.user && await pushPull(state)
  // post
  self && self.postMessage({ isSyncRedux: true,
    text: "dexiePushPull"
  })
}

async function dexieSignin () {
  // check
  const { rememberToken, user } = state
  if (!rememberToken || !user) {
    return
  }
  // get the matching user
  const users = await getData('users', { rememberToken })
  if (users.length === 0 || user.rememberToken !== state.user.rememberToken) {
    // trigger a first push pull to feed the dexie
    await dexiePushPull()
  } else {
    // if the user is already here we need just to trigger a
    // sync of the redux state
    self && self.postMessage({ isSyncRedux: true })
  }
  // setUser to set for the first time or just sync
  state.user && await setUser(state)
  // post
  self && self.postMessage({ text: "dexieSignin" })
}

async function dexieSignout () {
  // check
  const { rememberToken, user } = state
  // clear
  Object.keys(state).forEach(key => delete state[key])
  db.users.clear()
  // post
  self && self.postMessage({ text: "dexieSignout" })
}

self.addEventListener('message', event => {
  const { key, type } = event.data
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
    /*
    self.addEventListener('sync', function (event) {
      dexiePushPull()
    })
    */
  } else if (key === 'dexie-push-pull') {
    dexiePushPull()
  } else if (key === 'dexie-signin') {
    dexieSignin()
  } else if (key === 'dexie-signout') {
    dexieSignout()
  }
})
