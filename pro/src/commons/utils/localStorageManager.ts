import { storageAvailable } from './storageAvailable'

class LocalStorageManager {
  setItemIfNone(key: string, value: string): void {
    if (
      !storageAvailable('localStorage') ||
      localStorage.getItem(key) !== null
    ) {
      return
    }

    localStorage.setItem(key, value)
  }
}

export const localStorageManager = new LocalStorageManager()
