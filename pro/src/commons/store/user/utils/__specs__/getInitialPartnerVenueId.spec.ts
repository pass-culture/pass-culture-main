import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { VenueListItemLiteResponseModel } from '@/apiClient/v1'
import { getInitialPartnerVenueId } from '@/commons/store/user/utils/getInitialPartnerVenueId'
import { makeVenueListItemLiteResponseModel } from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

describe('getInitialPartnerVenueId', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Priority 1: venue ID from local storage', () => {
    it('should return venue ID from local storage when present and valid', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '123')

      const venues = [
        makeVenueListItemLiteResponseModel({ id: 123 }),
        makeVenueListItemLiteResponseModel({ id: 456 }),
      ]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBe(123)
    })

    it('should ignore venue ID from local storage when not found in venues list', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '999')

      const venues = [
        makeVenueListItemLiteResponseModel({ id: 123 }),
        makeVenueListItemLiteResponseModel({ id: 456 }),
      ]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBeNull()
    })

    it('should ignore invalid venue ID from local storage', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, 'invalid')

      const venues = [makeVenueListItemLiteResponseModel({ id: 123 })]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBe(123)
    })
  })

  describe('Priority 2: single venue auto-selection', () => {
    it('should return the only venue ID when user has exactly one venue', () => {
      const venues = [makeVenueListItemLiteResponseModel({ id: 789 })]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBe(789)
    })

    it('should return null when user has multiple venues', () => {
      const venues = [
        makeVenueListItemLiteResponseModel({ id: 123 }),
        makeVenueListItemLiteResponseModel({ id: 456 }),
      ]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBeNull()
    })
  })

  describe('Priority 3: no venue selection', () => {
    it('should return null when user has no venues', () => {
      const venues: VenueListItemLiteResponseModel[] = []

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBeNull()
    })
  })
})
