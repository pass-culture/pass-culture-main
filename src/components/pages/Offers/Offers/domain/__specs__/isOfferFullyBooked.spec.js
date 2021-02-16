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

  it('should be fully booked when every stock has 0 remaining quantity', () => {
    // given
    const stocks = [
      {
        remainingQuantity: 0,
      },
      {
        remainingQuantity: 0,
      },
    ]

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(true)
  })

  it('should not be fully booked when at least 1 stock has some remaining quantity', () => {
    // given
    const stocks = [
      {
        remainingQuantity: 3,
      },
      {
        remainingQuantity: 0,
      },
    ]

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(false)
  })

  it('should not be fully booked when at least 1 stock has unlimited remaining quantity', () => {
    // given
    const stocks = [
      {
        remainingQuantity: 'unlimited',
      },
      {
        remainingQuantity: 0,
      },
    ]

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(false)
  })
})
