import moment from 'moment-timezone'
import { getDisplayPrice } from '../../../../helpers/getDisplayPrice'
import parseHoursByStockId from '../parseHoursByStockId'

describe('src | components | booking | utils | parseHoursByStockId', () => {
  it('returns empty array if not valid', () => {
    const expected = []
    const now = moment()
    let value = null
    let result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = false
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = true
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = undefined
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = []
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = {}
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = { bookables: null }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = { date: null }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = { bookables: [], date: { date: now } }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = { bookables: [{ beginningDatetime: now }], date: { date: now } }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = {
      bookables: [{ beginningDatetime: now, id: 1234 }],
      date: { date: now },
    }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = {
      bookables: [{ beginningDatetime: 'Monday 12 June 2018', id: 1234 }],
      date: { date: now },
    }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
    value = {
      bookables: [{ beginningDatetime: now, id: 1234, price: 1 }],
      date: { date: 'not a moment object' },
    }
    result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
  })
  it('returns an array of objects with label and id', () => {
    const format = 'HH:mm'
    const now = moment()
    const price = 1
    const time = moment().format(format)
    const devisedPrice = getDisplayPrice(price)
    const expected = [{ id: 'AAAAA', label: `${time} - ${devisedPrice}` }]
    const value = {
      bookables: [
        { beginningDatetime: now },
        { beginningDatetime: now, id: 'AAAAA', price },
      ],
      date: { date: now },
    }
    const result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
  })
  it.skip('returns an array of objects in differents timezone', () => {
    const format = 'HH:mm'
    const now = moment()
    const nowtz = moment().tz('America/Los_Angeles')
    const price = 1
    const time = moment().format(format)
    const devisedPrice = getDisplayPrice(price)
    const expected = [{ id: 'AAAAA', label: `${time} - ${devisedPrice}` }]
    const value = {
      bookables: [
        { beginningDatetime: now },
        { beginningDatetime: now, id: 'AAAAA', price },
      ],
      date: { date: nowtz },
    }
    const result = parseHoursByStockId(value)
    expect(result).toStrictEqual(expected)
  })
})
