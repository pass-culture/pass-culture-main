import { storageAvailable } from './storageAvailable'

/**
 * **IMPORTANT**: Always prefix keys with `PASS_CULTURE_` to ease automatic cleanup of old keys.
 */
export enum LOCAL_STORAGE_KEY {
  SELECTED_VENUE_ID = 'PASS_CULTURE_SELECTED_VENUE_ID',
  SELECTED_ADMIN_OFFERER_ID = 'PASS_CULTURE_SELECTED_ADMIN_OFFERER_ID',
  LAST_VISITED_HOMEPAGE_TABS = 'PASS_CULTURE_LAST_VISITED_HOMEPAGE_TABS',
  NEW_STRUCTURE_OFFERER = 'PASS_CULTURE_NEW_STRUCTURE_OFFERER',
  NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS = 'PASS_CULTURE_NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS',
  NEW_STRUCTURE_ACTIVITY = 'PASS_CULTURE_NEW_STRUCTURE_ACTIVITY',
  SIMULATOR_SIRET = 'PASS_CULTURE_SIMULATOR_SIRET',
  SIMULATOR_ACTIVITY = 'PASS_CULTURE_SIMULATOR_ACTIVITY',
  SIMULATOR_OPEN_TO_PUBLIC = 'PASS_CULTURE_SIMULATOR_OPEN_TO_PUBLIC',
  SIMULATOR_TARGET_CUSTOMER = 'PASS_CULTURE_SIMULATOR_TARGET_CUSTOMER',
}

export enum COOKIES {
  DID_SKIP_ONBOARDING = 'DID_SKIP_ONBOARDING',
}

export const PASS_CULTURE_PREFIX = 'PASS_CULTURE_'

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

  clear: (): void => {
    if (!storageAvailable('localStorage')) {
      return
    }

    Object.keys(localStorage).forEach((key) => {
      localStorage.removeItem(key)
    })
  },
}
