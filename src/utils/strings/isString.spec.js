/* eslint no-console: 0, max-nested-callbacks: 0 */
import { isString } from './isString'

describe('src | utils | strings | isString', () => {
  it('return false', () => {
    const expected = false
    let value = false
    let received = isString(value)
    expect(received).toEqual(expected)
    value = null
    received = isString(value)
    expect(received).toEqual(expected)
    value = 1234
    received = isString(value)
    expect(received).toEqual(expected)
    value = 0
    received = isString(value)
    expect(received).toEqual(expected)
    value = undefined
    received = isString(value)
    expect(received).toEqual(expected)
    value = null
    received = isString(value)
    expect(received).toEqual(expected)
    value = []
    received = isString(value)
    expect(received).toEqual(expected)
    value = {}
    received = isString(value)
    expect(received).toEqual(expected)
  })
  it('return true', () => {
    const expected = true
    let value = ''
    let received = isString(value)
    expect(received).toEqual(expected)
    value = '     a'
    received = isString(value)
    expect(received).toEqual(expected)
    value = 'a string'
    received = isString(value)
    expect(received).toEqual(expected)
  })
})
