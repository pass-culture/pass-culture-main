export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then(registration => {
        registration.unregister()
      })
      .catch(error => {
        // FIX ME
        // eslint-disable-next-line
        console.error(error.message)
      })
  }
}
