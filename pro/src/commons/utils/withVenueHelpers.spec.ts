import { describe, expect, it } from 'vitest'

import { VenueState } from '@/apiClient/v1'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { withVenueHelpers } from './withVenueHelpers'

describe('withVenueHelpers', () => {
  describe('isClosed', () => {
    it('should be false when the venue has no state', () => {
      const venue = makeGetVenueResponseModel({ id: 1, state: null })

      expect(withVenueHelpers(venue).isClosed).toBe(false)
    })

    it('should be true when the venue is closing', () => {
      const venue = makeGetVenueResponseModel({
        id: 1,
        state: VenueState.CLOSING,
      })

      expect(withVenueHelpers(venue).isClosed).toBe(true)
    })

    it('should be true when the venue is closed', () => {
      const venue = makeGetVenueResponseModel({
        id: 1,
        state: VenueState.CLOSED,
      })

      expect(withVenueHelpers(venue).isClosed).toBe(true)
    })
  })

  describe('fullAddressAsString', () => {
    it('should join the street, postal code and city', () => {
      const venue = makeGetVenueResponseModel({ id: 1 })
      venue.location.street = '1 Rue de Paris'
      venue.location.postalCode = '75001'
      venue.location.city = 'Paris'

      expect(withVenueHelpers(venue).fullAddressAsString).toBe(
        '1 Rue de Paris, 75001 Paris'
      )
    })

    it('should omit the street when the venue location has none', () => {
      const venue = makeGetVenueResponseModel({ id: 1 })
      venue.location.street = null
      venue.location.postalCode = '75001'
      venue.location.city = 'Paris'

      expect(withVenueHelpers(venue).fullAddressAsString).toBe('75001 Paris')
    })
  })
})
