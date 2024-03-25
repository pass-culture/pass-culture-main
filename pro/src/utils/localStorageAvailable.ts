//  Function taken from MDN
//  (https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API#feature-detecting_localstorage)
//  Some browsers/OS will have local storage disabled which will raise errors when the code tries to access the storage
export function localStorageAvailable() {
  try {
    const storage = window.localStorage
    const x = '__storage_test__'
    storage.setItem(x, x)
    storage.removeItem(x)
    return true
  } catch (e) {
    return (
      e instanceof DOMException &&
      // everything except Firefox
      (e.code === 22 ||
        // Firefox
        e.code === 1014 ||
        // test name field too, because code might not be present
        // everything except Firefox
        e.name === 'QuotaExceededError' ||
        // Firefox
        e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
      // acknowledge QuotaExceededError only if there's something already stored
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      window.localStorage &&
      window.localStorage.length !== 0
    )
  }
}
