import { describe, expect, it } from 'vitest'

import type { VenueListItemLiteResponseModel } from '@/apiClient/v1'
import { getInitialPartnerVenueId } from '@/commons/store/user/utils/getInitialPartnerVenueId'
import { makeVenueListItemLiteResponseModel } from '@/commons/utils/factories/venueFactories'
import { LOCAL_STORAGE_KEY } from '@/commons/utils/localStorageManager'

describe('getInitialPartnerVenueId', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
  })
  describe('Priority 1 : URL param (backoffice)', () => {
    it('should return venue id from URL param', () => {
      window.history.pushState({}, '', '/?venue=10')

      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
        makeVenueListItemLiteResponseModel({ id: 20, managingOffererId: 2 }),
      ]

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBe(10)
    })
  })
  describe('Priority 2: first venue of a newly associated offerer', () => {
    it('should return the venue ID when new offerer has exactly one venue', () => {
      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
        makeVenueListItemLiteResponseModel({ id: 20, managingOffererId: 2 }),
      ]

      const result = getInitialPartnerVenueId(venues, 2)

      expect(result).toBe(20)
    })

    it('should return null when new offerer has multiple venues', () => {
      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
        makeVenueListItemLiteResponseModel({ id: 20, managingOffererId: 2 }),
        makeVenueListItemLiteResponseModel({ id: 30, managingOffererId: 2 }),
      ]

      const result = getInitialPartnerVenueId(venues, 2)

      expect(result).toBeNull()
    })

    it('should return null when no venue matches the new offerer', () => {
      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
      ]

      const result = getInitialPartnerVenueId(venues, 999)

      expect(result).toBeNull()
    })

    it('should take priority over local storage when offerer has one venue', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '10')

      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
        makeVenueListItemLiteResponseModel({ id: 20, managingOffererId: 2 }),
      ]

      const result = getInitialPartnerVenueId(venues, 2)

      expect(result).toBe(20)
    })

    it('should take priority over local storage even when returning null for multi-venue offerer', () => {
      localStorage.setItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID, '10')

      const venues = [
        makeVenueListItemLiteResponseModel({ id: 10, managingOffererId: 1 }),
        makeVenueListItemLiteResponseModel({ id: 20, managingOffererId: 2 }),
        makeVenueListItemLiteResponseModel({ id: 30, managingOffererId: 2 }),
      ]

      const result = getInitialPartnerVenueId(venues, 2)

      expect(result).toBeNull()
    })
  })

  describe('Priority 3: venue ID from local storage', () => {
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

  describe('Priority 4: single venue auto-selection', () => {
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

  describe('Priority 5: no venue selection', () => {
    it('should return null when user has no venues', () => {
      const venues: VenueListItemLiteResponseModel[] = []

      const result = getInitialPartnerVenueId(venues)

      expect(result).toBeNull()
    })
  })
})
