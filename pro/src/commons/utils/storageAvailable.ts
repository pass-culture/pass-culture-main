export type StorageType = 'localStorage' | 'sessionStorage'

// The probe writes a key, which fires a `storage` event in every other tab:
// run it once per storage type and cache the result.
const availabilityCache = new Map<StorageType, boolean>()

/**
 * Only meant to be used in tests, to re-run the probe between test cases.
 */
export function resetStorageAvailabilityCache(): void {
  availabilityCache.clear()
}

//  Function taken from MDN
//  (https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API#feature-detecting_localstorage)
//  Some browsers/OS will have local storage disabled which will raise errors when the code tries to access the storage
export function storageAvailable(type: StorageType): boolean {
  const cached = availabilityCache.get(type)
  if (cached !== undefined) {
    return cached
  }

  const isAvailable = probeStorage(type)
  availabilityCache.set(type, isAvailable)
  return isAvailable
}

function probeStorage(type: StorageType): boolean {
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
