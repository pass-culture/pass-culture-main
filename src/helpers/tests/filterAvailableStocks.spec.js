// jest --env=jsdom ./src/helpers/tests/filterAvailableStocks --watch
import moment from 'moment'
import filterAvailableStocks from '../filterAvailableStocks'

describe('src | helpers | filterAvailableStocks', () => {
  it('returns an empty array', () => {
    const expected = []
    let stocks = null
    let result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = false
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = {}
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = 1234
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = undefined
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = 'a string'
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = []
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
    stocks = [null, null]
    result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
  it('returns an array of objects without bookingLimitDatetime', () => {
    const stocks = [
      { notBookingLimitDatetime: true },
      { bookingLimitDatetime: null },
    ]
    const expected = [
      { notBookingLimitDatetime: true },
      { bookingLimitDatetime: null },
    ]
    const result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
  it('returns an array of objects with bookingLimitDatetime', () => {
    const unvaliddatea = moment()
    const unvaliddateb = moment().subtract(1, 'day')
    const validdatea = moment().add(2, 'day')
    const validdateb = moment().add(1, 'day')
    const stocks = [
      { bookingLimitDatetime: unvaliddatea },
      { bookingLimitDatetime: unvaliddateb },
      { bookingLimitDatetime: validdatea },
      { bookingLimitDatetime: validdateb },
      { bookingLimitDatetime: null },
    ]
    const expected = [
      { bookingLimitDatetime: validdatea },
      { bookingLimitDatetime: validdateb },
      { bookingLimitDatetime: null },
    ]
    const result = filterAvailableStocks(stocks)
    expect(result).toStrictEqual(expected)
  })
})
