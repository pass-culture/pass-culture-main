const BATCHSDK_MAJOR_VERSION = 2

importScripts("https://via.batch.com/v" + BATCHSDK_MAJOR_VERSION + "/worker.min.js")

const eventsList = ["pushsubscriptionchange", "push", "notificationclick", "message", "install"]
eventsList.forEach(eventName => {
  self.addEventListener(eventName, event => {
    event.waitUntil(self.handleBatchSDKEvent(eventName, event))
  })
})

