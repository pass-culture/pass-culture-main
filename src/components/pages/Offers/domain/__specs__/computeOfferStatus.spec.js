import { computeOfferStatus } from '../computeOfferStatus'

describe('compute offer status', () => {
  describe('when offer is inactive', () => {
    it('should be "inactive" prior to any other status', () => {
      // Given
      const offer = {
        isActive: false,
        hasBookingLimitDatetimesPassed: true,
        isFullyBooked: true,
      }
      const stocks = []

      // When
      const status = computeOfferStatus(offer, stocks)

      // Then
      expect(status).toBe('inactive')
    })
  })

  describe('when offer is active', () => {
    let offer

    beforeEach(() => {
      offer = {
        isActive: true,
        hasBookingLimitDatetimesPassed: false,
        isFullyBooked: false,
      }
    })

    it('should be "active" when offer is not expired nor sold out', () => {
      // Given
      const septemberSeventh2020 = 1599483337
      jest.spyOn(Date, 'now').mockImplementationOnce(() => septemberSeventh2020)

      const stocks = [
        {
          id: 1,
        },
        {
          id: 2,
        },
      ]

      // When
      const status = computeOfferStatus(offer, stocks)

      // Then
      expect(status).toBe('active')
    })

    describe('when offer is expired', () => {
      it('should be "expirée" even when offer is sold out', () => {
        // Given
        const stocks = [
          {
            id: 1,
          },
        ]
        offer.hasBookingLimitDatetimesPassed = true
        offer.isFullyBooked = true

        // When
        const status = computeOfferStatus(offer, stocks)

        // Then
        expect(status).toBe('expirée')
      })
    })

    describe('when offer is sold out but has not expired', () => {
      let offer

      beforeEach(() => {
        offer = {
          isActive: true,
          hasBookingLimitDatetimesPassed: false,
          isFullyBooked: true,
        }
      })

      it('should be "épuisée"', () => {
        // Given
        const stocks = [
          {
            id: 1,
          },
        ]

        // When
        const status = computeOfferStatus(offer, stocks)

        // Then
        expect(status).toBe('épuisée')
      })
    })

    describe('when offer has no stock yet', () => {
      it('should be "épuisée" even when offer is expired', () => {
        // Given
        const stocks = []
        offer.hasBookingLimitDatetimesPassed = true

        // When
        const status = computeOfferStatus(offer, stocks)

        // Then
        expect(status).toBe('épuisée')
      })
    })
  })
})
