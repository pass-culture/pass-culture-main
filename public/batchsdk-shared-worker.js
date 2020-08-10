// WARNING: This worker IS ONLY TO BE USED if you want to integrate Batch with your own
// service worker. Please use batchsdk-worker-loader.js otherwise
function setupSharedBatchSDK() {
  // Change this to switch the major Batch SDK version you want to use
  // This MUST match the version used in the bootstrap script you put in your page
  const BATCHSDK_MAJOR_VERSION = 2

  importScripts("https://via.batch.com/v" + BATCHSDK_MAJOR_VERSION + "/worker.min.js")

  const eventsList = ["pushsubscriptionchange", "push", "notificationclick", "message", "install"]
  eventsList.forEach(eventName => {
    self.addEventListener(eventName, event => {
      event.waitUntil(self.handleBatchSDKEvent(eventName, event))
    })
  })
}

setupSharedBatchSDK()
