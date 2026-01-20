import { storageAvailable } from './storageAvailable'

/**
 * **IMPORTANT**: Always prefix keys with `PASS_CULTURE_` to ease automatic cleanup of old keys.
 */
export enum LOCAL_STORAGE_KEY {
  SELECTED_VENUE_ID = 'PASS_CULTURE_SELECTED_VENUE_ID',
  SELECTED_ADMIN_OFFERER_ID = 'PASS_CULTURE_SELECTED_ADMIN_OFFERER_ID',

  // Legacy keys (will be removed in the future)
  /** @deprecated Will be removed in the future in favor of `SELECTED_VENUE_ID`. */
  SELECTED_OFFERER_ID = 'homepageSelectedOffererId',
}

export const localStorageManager = {
  getItem: (key: LOCAL_STORAGE_KEY): string | null => {
    if (!storageAvailable('localStorage')) {
      return null
    }

    return localStorage.getItem(key)
  },

  setItem: (key: LOCAL_STORAGE_KEY, value: string): void => {
    if (!storageAvailable('localStorage')) {
      return
    }

    localStorage.setItem(key, value)
  },

  removeItem: (key: LOCAL_STORAGE_KEY): void => {
    if (!storageAvailable('localStorage')) {
      return
    }

    localStorage.removeItem(key)
  },
}
