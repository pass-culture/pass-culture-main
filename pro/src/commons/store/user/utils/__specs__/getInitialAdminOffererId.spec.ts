import { vi } from 'vitest'

import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import { localStorageManager } from '@/commons/utils/localStorageManager'

import { getInitialAdminOffererId } from '../getInitialAdminOffererId'

vi.mock('@/commons/utils/localStorageManager', () => ({
  localStorageManager: {
    getItem: vi.fn(),
  },
  LOCAL_STORAGE_KEY: {
    SELECTED_ADMIN_OFFERER_ID: 'SELECTED_ADMIN_OFFERER_ID',
  },
}))

describe('getInitialAdminOffererId', () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should return null when offererNames is empty', () => {
    const result = getInitialAdminOffererId([])

    expect(result).toBeNull()
  })

  it('should return saved offerer id when present in offererNames', () => {
    vi.spyOn(localStorageManager, 'getItem').mockReturnValue('123')
    const offerers = [
      getOffererNameFactory({ id: 123 }),
      getOffererNameFactory({ id: 456 }),
    ]

    const result = getInitialAdminOffererId(offerers)

    expect(result).toBe(123)
  })

  it('should return default (first) offerer id when no saved id', () => {
    vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)
    const offerers = [
      getOffererNameFactory({ id: 123 }),
      getOffererNameFactory({ id: 456 }),
    ]

    const result = getInitialAdminOffererId(offerers)

    expect(result).toBe(123)
  })

  it('should return default (first) offerer id when saved id is not in offererNames', () => {
    vi.spyOn(localStorageManager, 'getItem').mockReturnValue('999')
    const offerers = [
      getOffererNameFactory({ id: 123 }),
      getOffererNameFactory({ id: 456 }),
    ]

    const result = getInitialAdminOffererId(offerers)

    expect(result).toBe(123)
  })
})
