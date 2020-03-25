import filterRemainingStocks from '../filterRemainingStocks'

describe('src | filterRemainingStocks', () => {
  it('should return an array containing stocks with remaining quantity', () => {
    // given
    const stocks = [
      { id: 1, remainingQuantity: 1 },
      { id: 2, remainingQuantity: 'unlimited' },
      { id: 3, remainingQuantity: 0 },
    ]

    // when
    const result = filterRemainingStocks(stocks)

    // then
    expect(result).toHaveLength(2)
    expect(result).toStrictEqual([
      { id: 1, remainingQuantity: 1 },
      { id: 2, remainingQuantity: 'unlimited' },
    ])
  })
})
