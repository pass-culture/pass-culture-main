// jest --env=jsdom ./src/helpers/tests/getPriceRangeFromStocks --watch
import getPriceRangeFromStocks from '../getPriceRangeFromStocks'

describe('src | helpers | getPriceRangeFromStocks', () => {
  it('returns an empty array', () => {
    const expected = []
    let stocks = []
    let result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = null
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = undefined
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = 1234
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = 'a string'
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = false
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = {}
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = [{}, { available: null }, { available: 0 }]
    result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
  it('returns an array of prices (2)', () => {
    const stocks = [
      {},
      { available: null },
      { available: 0 },
      { available: 1, price: 0 },
      { available: 10, price: 100 },
    ]
    const expected = [0, 100]
    const result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
  it('returns an array of prices (...n)', () => {
    const stocks = [
      {},
      { available: null },
      { available: 0 },
      { available: 1, price: 0 },
      { available: 10, price: 10 },
      { available: 100, price: 100 },
      { available: 1000, price: 1000 },
    ]
    const expected = [0, 10, 100, 1000]
    const result = getPriceRangeFromStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
})
