import filterRemainingStocks from '../filterRemainingStocks'

describe('src | filterRemainingStocks', () => {
  it('should return an array containing stocks with remaining quantity', () => {
    // given
    const stocks = [
      { id: 1, remainingQuantityOrUnlimited: 1 },
      { id: 2, remainingQuantityOrUnlimited: 'unlimited' },
      { id: 3, remainingQuantityOrUnlimited: 0 },
    ]

    // when
    const result = filterRemainingStocks(stocks)

    // then
    expect(result).toHaveLength(2)
    expect(result).toStrictEqual([
      { id: 1, remainingQuantityOrUnlimited: 1 },
      { id: 2, remainingQuantityOrUnlimited: 'unlimited' },
    ])
  })
})
