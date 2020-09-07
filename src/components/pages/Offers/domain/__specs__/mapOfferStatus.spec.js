import { mapOfferStatus } from '../mapOfferStatus'

describe('map offer status', () => {
  describe('when offer is deactivated', () => {
    let isOfferActive

    beforeEach(() => {
      isOfferActive = false
    })

    it('should return "désactivée"', () => {
      // Given
      const stocks = [
        {
          remainingQuantity: 1,
          bookingLimitDatetime: null,
        },
      ]

      // When
      const status = mapOfferStatus(isOfferActive, stocks)

      // Then
      expect(status).toBe('désactivée')
    })

    it('should return "désactivée" even when offer is expired', () => {
      // Given
      const stocks = [
        {
          remainingQuantity: 5,
          bookingLimitDatetime: '2002-09-18T18:30:00Z',
        },
      ]

      // When
      const status = mapOfferStatus(isOfferActive, stocks)

      // Then
      expect(status).toBe('désactivée')
    })

    it('should return "désactivée" even when offer is sold out', () => {
      // Given
      const stocks = [
        {
          remainingQuantity: 0,
          bookingLimitDatetime: null,
        },
      ]

      // When
      const status = mapOfferStatus(isOfferActive, stocks)

      // Then
      expect(status).toBe('désactivée')
    })
  })

  describe('when offer is active', () => {
    let isOfferActive

    beforeEach(() => {
      isOfferActive = true
    })

    it('should return "active"', () => {
      // Given
      const septemberSeventh2020 = 1599483337
      jest.spyOn(Date, 'now').mockImplementationOnce(() => septemberSeventh2020)

      const stocks = [
        {
          remainingQuantity: 'unlimited',
          bookingLimitDatetime: '2020-10-18T18:30:00Z',
        },
        {
          remainingQuantity: 0,
          bookingLimitDatetime: '2020-07-18T18:30:00Z',
        },
      ]

      // When
      const status = mapOfferStatus(isOfferActive, stocks)

      // Then
      expect(status).toBe('active')
    })

    describe('when offer is expired', () => {
      let stocks

      beforeEach(() => {
        stocks = [
          {
            remainingQuantity: 1,
            bookingLimitDatetime: '2002-09-18T18:30:00Z',
          },
        ]
      })

      it('should return "expirée"', () => {
        // When
        const status = mapOfferStatus(isOfferActive, stocks)

        // Then
        expect(status).toBe('expirée')
      })

      it('should return "expirée" even when offer is sold out', () => {
        // Given
        stocks[0].remainingQuantity = 0

        // When
        const status = mapOfferStatus(isOfferActive, stocks)

        // Then
        expect(status).toBe('expirée')
      })
    })

    describe('when offer is sold out', () => {
      it('should return "épuisée"', () => {
        // Given
        const stocks = [
          {
            bookingLimitDatetime: null,
            remainingQuantity: 0,
          },
          {
            bookingLimitDatetime: null,
            remainingQuantity: 0,
          },
        ]

        // When
        const status = mapOfferStatus(isOfferActive, stocks)

        // Then
        expect(status).toBe('épuisée')
      })
    })

    describe('when offer has no stock yet', () => {
      it('should return "épuisée"', () => {
        // Given
        const stocks = []

        // When
        const status = mapOfferStatus(isOfferActive, stocks)

        // Then
        expect(status).toBe('épuisée')
      })
    })
  })
})
