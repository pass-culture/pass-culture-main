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
  postMessage({ isSyncRedux: true,
    text: "dexiePushPull"
  })
}

async function dexieSignin () {
  // check
  const { user } = state
  console.log('USER DEXIE', user)
  if (!user) {
    return
  }
  // get the matching user
  const users = await getData('users', { id: user.id })
  if (users.length === 0) {
    // trigger a first push pull to feed the dexie
    await dexiePushPull()
  } else {
    // if the user is already here we need just to trigger a
    // sync of the redux state
    postMessage({ isSyncRedux: true })
  }
  // setUser to set for the first time or just sync
  state.user && await setUser(state)
  // post
  postMessage({ text: "dexieSignin" })
}

async function dexieSignout () {
  // clear
  Object.keys(state).forEach(key => delete state[key])
  db.users.clear()
  // post
  postMessage({ text: "dexieSignout" })
}

// eslint-disable-next-line no-restricted-globals
self.addEventListener('message', event => {
  const { key, log, type } = event.data
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
    addEventListener('sync', function (event) {
      dexiePushPull()
    })
    */
  } else if (key === 'dexie-ping') {
    console.log('DEXIE WORKER PING!')
    postMessage({ log: "dexiePing" })
  } else if (key === 'dexie-push-pull') {
    dexiePushPull()
  } else if (key === 'dexie-signin') {
    dexieSignin()
  } else if (key === 'dexie-signout') {
    dexieSignout()
  }
})
