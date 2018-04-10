/* global self */
/* eslint no-restricted-globals: ["off", "self"] */
import { db,
  pushPull,
  setUser
} from './data'

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
    this.receiveMessage({ isSyncRedux: true,
      text: "dexiePushPull"
    })
  }
  async dexieSignin () {
    // check
    const { user } = this.state
    if (!user) {
      return
    }
    // do push pull to be sure to sync
    await pushPull(this.state)
    // setUser to set for the first time or just sync
    this.state.user && await setUser(this.state)
    // sync the redux state
    this.receiveMessage({ isSyncRedux: true, text: "dexieSignin" })
  }
  dexieSignout () {
    // clear
    Object.keys(this.state).forEach(key => delete this.state[key])
    db.users.clear()
    // post
    this.receiveMessage({ text: "dexieSignout" })
  }
  onMessage = event => {
    const { key } = event.data
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

let DexieWorker
if (process.env.HAS_WORKERS) {
  const dexieWrapper = new DexieWrapper(self)
  self.addEventListener('message', dexieWrapper.onMessage)
} else {
  DexieWorker = DexieWrapper
}

export default DexieWorker
