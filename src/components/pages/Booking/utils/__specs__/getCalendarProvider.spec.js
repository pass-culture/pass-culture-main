import moment from 'moment'

import getCalendarProvider from '../getCalendarProvider'

describe('src | components | booking | utils', () => {
  it('return empty array if invalid args', () => {
    let value = false
    let result = getCalendarProvider(value)
    expect(result).toStrictEqual([])

    value = true
    result = getCalendarProvider(value)
    expect(result).toStrictEqual([])

    value = {}
    result = getCalendarProvider(value)
    expect(result).toStrictEqual([])

    value = null
    result = getCalendarProvider(value)
    expect(result).toStrictEqual([])

    value = undefined
    result = getCalendarProvider(value)
    expect(result).toStrictEqual([])

    value = 'a string'
    result = getCalendarProvider(value)
    expect(result).toStrictEqual([])
  })

  it('return empty array if args is missing bookables', () => {
    const value = {}

    // when
    const result = getCalendarProvider(value)

    // then
    expect(result).toStrictEqual([])
  })

  it('return empty array if bookables is empty array', () => {
    const value = { bookables: [] }

    // when
    const result = getCalendarProvider(value)

    // then
    expect(result).toStrictEqual([])
  })

  it('return empty array if bookables has no { beginningDatetime }', () => {
    const value = { bookables: [undefined, null, false, {}, []] }

    // when
    const result = getCalendarProvider(value)

    // then
    expect(result).toStrictEqual([])
  })

  it('return empty array if beginningDatetime not a moment object', () => {
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

    // when
    const result = getCalendarProvider(value)

    // then
    expect(result).toStrictEqual([])
  })

  it('return filtered array with beginningDatetime', () => {
    const mom = moment()
    const mom2 = moment()
    const value = {
      bookables: [{ beginningDatetime: mom2 }, { beginningDatetime: mom }],
    }

    // when
    const result = getCalendarProvider(value)

    // then
    expect(result).toStrictEqual([mom2, mom])
  })
})
