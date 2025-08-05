//  Function taken from MDN
//  (https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API#feature-detecting_localstorage)
//  Some browsers/OS will have local storage disabled which will raise errors when the code tries to access the storage
export function storageAvailable(
  type: 'localStorage' | 'sessionStorage'
): boolean {
  let storage: Storage | null = null
  try {
    storage = window[type]
    const x = '__storage_test__'
    storage.getItem(x)
    storage.setItem(x, x)
    storage.removeItem(x)
    return true
  } catch (e) {
    return Boolean(
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
        storage &&
        storage.length !== 0
    )
  }
}
