import { vi } from 'vitest'

import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  makeGetVenueManagingOffererResponseModel,
  makeGetVenueResponseModel,
} from '@/commons/utils/factories/venueFactories'
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
  const offererNames = [
    getOffererNameFactory({ id: 100 }),
    getOffererNameFactory({ id: 200 }),
  ]

  describe('Priority 1: localStorage', () => {
    it('should return saved offerer id when present in offererNamesValidated', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue('100')

      const result = getInitialAdminOffererId({
        offererNames,
        selectedVenue: null,
      })

      expect(result).toBe(100)
    })

    it('should call handleUnexpectedError and return null when saved id is not in offererNamesValidated', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue('999')

      const result = getInitialAdminOffererId({
        offererNames,
        selectedVenue: null,
      })

      expect(result).toBeNull()
    })
  })

  describe('Priority 2: selectedVenue parent offerer', () => {
    it('should return selectedVenue parent offerer id when no localStorage and venue is selected', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)
      const selectedVenue = makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({ id: 100 }),
      })

      const result = getInitialAdminOffererId({
        offererNames,
        selectedVenue,
      })

      expect(result).toBe(100)
    })

    it('should call handleUnexpectedError and return null when selectedVenue parent offerer is not in offererNamesValidated', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)
      const selectedVenue = makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 999,
        }),
      })

      const result = getInitialAdminOffererId({
        offererNames,
        selectedVenue,
      })

      expect(result).toBeNull()
    })
  })

  describe('Priority 3: first offerer', () => {
    it('should return first offerer id when no localStorage and no selectedVenue', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)

      const result = getInitialAdminOffererId({
        offererNames,
        selectedVenue: null,
      })

      expect(result).toBe(100)
    })
  })

  describe('Priority 4: no offerers', () => {
    it('should return null when offererNames is empty', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)

      const result = getInitialAdminOffererId({
        offererNames: [],
        selectedVenue: null,
      })

      expect(result).toBeNull()
    })
  })
})
