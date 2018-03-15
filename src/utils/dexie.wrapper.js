import { db,
  getData,
  pushPull,
  setUser
} from './dexie.data'

// in the case where we don't actually
class DexieWrapper {
  constructor (worker) {
    this.state = {}
    this.worker = worker
  }

  postMessage = data => {
    this.onMessage({ data })
  }

  receiveMessage = message => {
    this.worker
      ? this.worker.postMessage(message)
      : this.onmessage({ data: message })
  }

  async dexiePushPull () {
    // pull
    this.state.user && await pushPull(this.state)
    // post
    (this.isWorker ? this.worker.postMessage : this.onmessage)({ isSyncRedux: true,
      text: "dexiePushPull"
    })
  }
  async dexieSignin () {
    // check
    const { user } = this.state
    if (!user) {
      return
    }
    // get the matching user
    const users = await getData('users', { id: user.id })
    if (users.length === 0) {
      // trigger a first push pull to feed the dexie
      await this.dexiePushPull()
    } else if (users[0].id === user.id) {
      // if the user is already here we need just to trigger a
      // sync of the redux state
      this.receiveMessage({ isSyncRedux: true })
    } else {
      console.warn('signin with a different user from the dexie!')
    }
    // setUser to set for the first time or just sync
    this.state.user && await setUser(this.state)
    // post
    this.receiveMessage({ text: "dexieSignin" })
  }
  dexieSignout () {
    // clear
    Object.keys(this.state).forEach(key => delete this.state[key])
    db.users.clear()
    // post
    this.receiveMessage({ text: "dexieSignout" })
  }
  onMessage = event => {
    const { key, log, type } = event.data
    // check
    if (!key) {
      console.warn('you need to define a key in event.data')
      return
    }
    // update
    event.data.state &&
      Object.keys(event.data.state).length > 0 &&
      Object.assign(this.state, event.data.state, this.state)
    // switch
    if (key === 'dexie-init') {
      this.worker.addEventListener('sync', this.dexiePushPull)
    } else if (key === 'dexie-ping') {
      console.log('DEXIE WORKER PING!')
      this.receiveMessage({ log: "dexiePing" })
    } else if (key === 'dexie-push-pull') {
      this.dexiePushPull()
    } else if (key === 'dexie-signin') {
      this.dexieSignin()
    } else if (key === 'dexie-signout') {
      this.dexieSignout()
    }
  }
}

export default DexieWrapper
