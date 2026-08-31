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
      e &&
        typeof e === 'object' &&
        'name' in e &&
        e.name === 'QuotaExceededError' &&
        storage &&
        storage.length !== 0
    )
  }
}
