import { computeOfferStatus } from '../computeOfferStatus'

describe('compute offer status', () => {
  describe('when offer is inactive', () => {
    it('should be "validée" if also validated', () => {
      // Given
      const offer = {
        isActive: false,
        validation: 'VALIDATED',
      }
      const stocks = []

      // When
      const status = computeOfferStatus(offer, stocks)

      // Then
      expect(status).toBe('validée')
    })

    it('should be "refusée" if validation is rejected', () => {
      // Given
      const offer = {
        isActive: false,
        validation: 'REJECTED',
      }
      const stocks = []

      // When
      const status = computeOfferStatus(offer, stocks)

      // Then
      expect(status).toBe('refusée')
    })
  })

  describe('when offer is active', () => {
    let offer

    beforeEach(() => {
      offer = {
        isActive: true,
        hasBookingLimitDatetimesPassed: false,
        isFullyBooked: false,
        validation: 'VALIDATED',
      }
    })

    it('should be "active" when offer is not expired nor sold out', () => {
      // Given
      const septemberSeventh2020 = 1599483337
      jest.spyOn(Date, 'now').mockImplementationOnce(() => septemberSeventh2020)

      const stocks = [
        {
          id: 1,
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 'unlimited',
        },
        {
          id: 2,
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 'unlimited',
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
      it('should be "épuisée"', () => {
        // Given
        const stocks = [
          {
            id: 1,
            remainingQuantity: 0,
          },
        ]
        offer.isFullyBooked = true

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

    describe('when offer is awaiting', () => {
      it('should be "en attente"', () => {
        // Given
        offer.validation = 'AWAITING'
        const stocks = []

        // When
        const status = computeOfferStatus(offer, stocks)

        // Then
        expect(status).toBe('en attente')
      })
    })
  })
})
