export const unregister = () => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        registration.unregister()
      })
      .catch((error) => {
        // FIX ME
        // eslint-disable-next-line
        console.error(error.message)
      })
  }
}
