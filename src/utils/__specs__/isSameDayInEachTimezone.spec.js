import moment from 'moment-timezone'

import isSameDayInEachTimezone from '../isSameDayInEachTimezone'

describe('src | helpers | isSameDayInEachTimezone', () => {
  it('return false, values should be moment object', () => {
    const expected = false
    const dateb = moment()
    let datea = null
    let result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = []
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = false
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = undefined
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = 1234
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = {}
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = { format: () => {} }
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
    datea = Date.now()
    result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
  })

  it('return true, dates are same day in same timezone', () => {
    const expected = true
    let date = new Date('2018-12-25 1:00:00')
    const datea = moment(date)
    date = new Date('2018-12-25 23:00:00')
    const dateb = moment(date)
    const result = isSameDayInEachTimezone(datea, dateb)
    expect(result).toStrictEqual(expected)
  })
})
