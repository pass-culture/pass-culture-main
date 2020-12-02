console.log('Old script detected')
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.ready
    .then(registration => {
      console.log('Unregister service worker')
      registration.unregister()
      console.log('Start reloading')
      window.location.reload()
      console.log('Page reloaded')
    })
    .catch(error => {
      console.error(error.message)
    })
}
