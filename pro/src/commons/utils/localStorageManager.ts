import { storageAvailable } from './storageAvailable'

/**
 * **IMPORTANT**: Always prefix keys with `PASS_CULTURE_` to ease automatic cleanup of old keys.
 */
export enum LOCAL_STORAGE_KEY {
  SELECTED_VENUE_ID = 'PASS_CULTURE_SELECTED_VENUE_ID',
  SELECTED_ADMIN_OFFERER_ID = 'PASS_CULTURE_SELECTED_ADMIN_OFFERER_ID',
  LAST_VISITED_HOMEPAGE_TABS = 'PASS_CULTURE_LAST_VISITED_HOMEPAGE_TABS',
  HAS_SEEN_VOLUNTEERING_SECTION = 'PASS_CULTURE_HAS_SEEN_VOLUNTEERING_SECTION',
  NEW_STRUCTURE_OFFERER = 'PASS_CULTURE_NEW_STRUCTURE_OFFERER',
  NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS = 'PASS_CULTURE_NEW_STRUCTURE_OFFERER_INITIAL_ADDRESS',
  NEW_STRUCTURE_ACTIVITY = 'PASS_CULTURE_NEW_STRUCTURE_ACTIVITY',
}

// Legacy keys which don't follow the PASS_CULTURE_PREFIX prefix pattern
const LOCAL_STORAGE_KEYS_TO_PRUNE = ['homepageSelectedOffererId']

export const PASS_CULTURE_PREFIX = 'PASS_CULTURE_'

/**
 * Keys that should persist across logout.
 */
const PERSISTENT_KEYS = new Set<string>([
  // TODO (tpommellet, 2026-05-01): Remove this key once volunteering GTM period is over.
  LOCAL_STORAGE_KEY.HAS_SEEN_VOLUNTEERING_SECTION,
])

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

  clearPassCultureKeys: (): void => {
    if (!storageAvailable('localStorage')) {
      return
    }

    Object.keys(localStorage)
      .filter(
        (key) =>
          (key.startsWith(PASS_CULTURE_PREFIX) && !PERSISTENT_KEYS.has(key)) ||
          LOCAL_STORAGE_KEYS_TO_PRUNE.includes(key)
      )
      .forEach((key) => {
        localStorage.removeItem(key)
      })
  },
}
