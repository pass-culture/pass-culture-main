import { IS_DEV } from './config'
import { clear, db, fetch, pull } from './dexie'

const dexieSwUrl = `${process.env.PUBLIC_URL}/dexie-service-worker.js`

// use messagechannel to communicate
function sendMessageToServiceWorker (message) {
  return new Promise((resolve, reject) => {
    // Create a Message Channel
    const swMessageChannel = new MessageChannel()
    // Handler for recieving message reply from service worker
    swMessageChannel.port1.onmessage = event => {
      if(event.data.error) {
        reject(event.data.error)
      } else {
        console.log('SA MERE', event.data)
        resolve(event.data)
      }
    }
    navigator.serviceWorker.controller.postMessage(message, [swMessageChannel.port2])
  })
}

// send message to serviceWorker
// you can see that i add a parse argument
// this is use to tell the serviceworker how to parse our data
export function sync (key, store) {
  return sendMessageToServiceWorker({ key, store, type: 'sync' })
}

export default async function registerDexieServiceWorker() {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register(dexieSwUrl)
    if (!navigator.serviceWorker.ready) {
      return
    }
    sync("dexie-init", { text: "allez OUAI" })
    return registration
  }
}



if (IS_DEV) {
  window.clearDexie = clear
  window.dexieDb = db
  window.fetchDexie = fetch
  window.pullDexie = pull
}
