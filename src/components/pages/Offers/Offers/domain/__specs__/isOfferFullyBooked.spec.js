import { isOfferFullyBooked } from '../isOfferFullyBooked'

describe('isOfferFullyBooked', () => {
  it('should be fully booked when offer has no stocks yet', () => {
    // given
    const stocks = []

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(true)
  })

  describe('when every stock in the future has 0 remaining quantity', () => {
    it('should be fully bookend if no stocks in the past', () => {
      // given
      const stocks = [
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
      ]

      // when
      const isFullyBooked = isOfferFullyBooked(stocks)

      // then
      expect(isFullyBooked).toBe(true)
    })

    it('should be fully bookend if a stock in the past has a remaining quantity', () => {
      // given
      const stocks = [
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
        {
          hasBookingLimitDatetimePassed: true,
          remainingQuantity: 10,
        },
      ]

      // when
      const isFullyBooked = isOfferFullyBooked(stocks)

      // then
      expect(isFullyBooked).toBe(true)
    })

    it('should be fully bookend if a stock in the past has an unlimited quantity', () => {
      // given
      const stocks = [
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
        {
          hasBookingLimitDatetimePassed: true,
          remainingQuantity: 'unlimited',
        },
      ]

      // when
      const isFullyBooked = isOfferFullyBooked(stocks)

      // then
      expect(isFullyBooked).toBe(true)
    })
  })

  it('should not be fully booked when at least 1 stock in the future has some remaining quantity', () => {
    // given
    const stocks = [
      {
        hasBookingLimitDatetimePassed: false,
        remainingQuantity: 3,
      },
      {
        hasBookingLimitDatetimePassed: false,
        remainingQuantity: 0,
      },
    ]

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(false)
  })

  it('should not be fully booked when at least 1 stock in the future has unlimited remaining quantity', () => {
    // given
    const stocks = [
      {
        hasBookingLimitDatetimePassed: false,
        remainingQuantity: 'unlimited',
      },
      {
        hasBookingLimitDatetimePassed: false,
        remainingQuantity: 0,
      },
    ]

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(false)
  })
})
