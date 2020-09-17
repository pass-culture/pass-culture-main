import { isOfferFullyBooked } from '../isOfferFullyBooked'

describe('isOfferFullyBooked', () => {
  it('should return true when offer has no stocks yet', () => {
    // given
    const stocks = []

    // when
    const isFullyBooked = isOfferFullyBooked(stocks)

    // then
    expect(isFullyBooked).toBe(true)
  })

  it('should return true when every stock has 0 remainingQuantity', () => {
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

  it('should return false when at least 1 stock has some remainingQuantity', () => {
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

  it('should return false when at least 1 stock has unlimited remainingQuantity', () => {
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
