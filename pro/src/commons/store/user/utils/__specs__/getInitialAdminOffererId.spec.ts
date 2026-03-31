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
        selectedPartnerVenue: null,
      })

      expect(result).toBe(100)
    })

    it('should fall through to next priority when saved id is not in offererNames', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue('999')

      const result = getInitialAdminOffererId({
        offererNames,
        selectedPartnerVenue: null,
      })

      expect(result).toBe(100)
    })
  })

  describe('Priority 2: selectedPartnerVenue parent offerer', () => {
    it('should return selectedPartnerVenue parent offerer id when no localStorage and venue is selected', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)
      const selectedPartnerVenue = makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({ id: 100 }),
      })

      const result = getInitialAdminOffererId({
        offererNames,
        selectedPartnerVenue,
      })

      expect(result).toBe(100)
    })

    it('should return null when selectedPartnerVenue parent offerer is not in offererNames', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)
      const selectedPartnerVenue = makeGetVenueResponseModel({
        id: 101,
        managingOfferer: makeGetVenueManagingOffererResponseModel({
          id: 999,
        }),
      })

      const result = getInitialAdminOffererId({
        offererNames,
        selectedPartnerVenue,
      })

      expect(result).toBeNull()
    })
  })

  describe('Priority 3: first offerer', () => {
    it('should return first offerer id when no localStorage and no selectedPartnerVenue', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)

      const result = getInitialAdminOffererId({
        offererNames,
        selectedPartnerVenue: null,
      })

      expect(result).toBe(100)
    })
  })

  describe('Priority 4: no offerers', () => {
    it('should return null when offererNames is empty', () => {
      vi.spyOn(localStorageManager, 'getItem').mockReturnValue(null)

      const result = getInitialAdminOffererId({
        offererNames: [],
        selectedPartnerVenue: null,
      })

      expect(result).toBeNull()
    })
  })
})
