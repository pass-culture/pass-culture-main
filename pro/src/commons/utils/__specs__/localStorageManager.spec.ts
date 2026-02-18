import { vi } from 'vitest'

import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import * as storageAvailableModule from '@/commons/utils/storageAvailable'

vi.mock('@/commons/utils/storageAvailable', () => ({
  storageAvailable: vi.fn(),
}))

describe('localStorageManager', () => {
  const key = LOCAL_STORAGE_KEY.SELECTED_VENUE_ID

  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
  })

  it('should delegate all methods to Local Storage when available', () => {
    vi.spyOn(storageAvailableModule, 'storageAvailable').mockReturnValue(true)

    expect(localStorageManager.getItem(key)).toBeNull()

    localStorageManager.setItem(key, '123')
    expect(localStorage.getItem(key)).toBe('123')
    expect(localStorageManager.getItem(key)).toBe('123')

    localStorageManager.setItem(key, '456')
    expect(localStorage.getItem(key)).toBe('456')

    localStorageManager.removeItem(key)
    expect(localStorage.getItem(key)).toBeNull()
    expect(localStorageManager.getItem(key)).toBeNull()
  })

  it('should be a no-op for all methods when Local Storage is not available', () => {
    vi.spyOn(storageAvailableModule, 'storageAvailable').mockReturnValue(false)

    localStorage.setItem(key, 'seed')

    expect(localStorageManager.getItem(key)).toBeNull()

    localStorageManager.setItem(key, 'new')
    expect(localStorage.getItem(key)).toBe('seed')

    localStorageManager.removeItem(key)
    expect(localStorage.getItem(key)).toBe('seed')

    localStorageManager.clearPassCultureKeys()
    expect(localStorage.getItem('PASS_CULTURE_SELECTED_VENUE_ID')).toBe('seed')
  })

  it('should remove only keys prefixed with PASS_CULTURE_ when calling clearPassCultureKeys', () => {
    vi.spyOn(storageAvailableModule, 'storageAvailable').mockReturnValue(true)

    localStorage.setItem('PASS_CULTURE_SELECTED_VENUE_ID', 'venue-1')
    localStorage.setItem(
      'PASS_CULTURE_LAST_VISITED_HOMEPAGE_TABS',
      'tab-collective'
    )
    localStorage.setItem('homepageSelectedOffererId', '42')
    localStorage.setItem('someOtherKey', 'value')

    localStorageManager.clearPassCultureKeys()

    expect(localStorage.getItem('PASS_CULTURE_SELECTED_VENUE_ID')).toBeNull()
    expect(
      localStorage.getItem('PASS_CULTURE_LAST_VISITED_HOMEPAGE_TABS')
    ).toBeNull()
    expect(localStorage.getItem('homepageSelectedOffererId')).toBe('42')
    expect(localStorage.getItem('someOtherKey')).toBe('value')
  })
})
