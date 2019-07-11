import moment from 'moment'

import getCalendarProvider from '../getCalendarProvider'

describe('src | components | booking | utils', () => {
  it('return empty array if invalid args', () => {
    const expected = []
    let value = false
    let result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
    value = true
    result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
    value = {}
    result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
    value = null
    result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
    value = undefined
    result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
    value = 'a string'
    result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
  it('return empty array if args is missing bookables', () => {
    const expected = []
    const value = {}
    const result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
  it('return empty array if bookables is empty array', () => {
    const expected = []
    const value = { bookables: [] }
    const result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
  it('return empty array if bookables has no { beginningDatetime }', () => {
    const expected = []
    const value = { bookables: [undefined, null, false, {}, []] }
    const result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
  it('return empty array if beginningDatetime not a moment object', () => {
    const expected = []
    const value = {
      bookables: [
        { beginningDatetime: {} },
        { beginningDatetime: false },
        { beginningDatetime: null },
        { beginningDatetime: undefined },
        { beginningDatetime: new Date() },
        { beginningDatetime: new Date().toISOString() },
      ],
    }
    const result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
  it('return filtered array with beginningDatetime', () => {
    const mom = moment()
    const mom2 = moment()
    const expected = [mom2, mom]
    const value = {
      bookables: [{ beginningDatetime: mom2 }, { beginningDatetime: mom }],
    }
    const result = getCalendarProvider(value)
    expect(result).toStrictEqual(expected)
  })
})
