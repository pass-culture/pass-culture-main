import { IS_DEV } from './config'
import { clear, db, fetch, pull } from './dexie'

const dexieSwUrl = `${process.env.PUBLIC_URL}/dexie-service-worker.js`

export default async function registerDexieServiceWorker() {


  // db.configs.add({ id: Math.random() })
  db.configs.hook('creating', function (modifications, primKey, obj, transaction) {
    console.log('OUSQDQDS')
  })
  /*
  db.configs.hook('updating', function (modifications, primKey, obj, transaction) {
    console.log('OUSQDQDS')
  })
  */

  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register(dexieSwUrl)

    navigator.serviceWorker.addEventListener('message', function (event) {
      console.log("Client 1 Received Message: " + event.data)
      // event.ports[0].postMessage("Client 1 Says 'Hello back!'");
    })

    if (!navigator.serviceWorker.ready) {
      return
    }
    registration.sync.register('dexie-pull')
    return registration
  }
}



if (IS_DEV) {
  window.clearDexie = clear
  window.dexieDb = db
  window.fetchDexie = fetch
  window.pullDexie = pull
}
