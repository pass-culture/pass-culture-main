/* eslint no-console: 0, max-nested-callbacks: 0 */
import { hasNumber } from './hasNumber'

describe('src | utils | strings | hasNumber', () => {
  it('return false', () => {
    const expected = false
    let value = ''
    let received = hasNumber(value)
    expect(received).toEqual(expected)
    value = false
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = null
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = 1234
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = 0
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = undefined
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = null
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = []
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = {}
    received = hasNumber(value)
    expect(received).toEqual(expected)
    value = '      '
    received = hasNumber(value)
    expect(received).toEqual(expected)
  })
  it('return true', () => {
    const expected = true
    let value = '1'
    let received = hasNumber(value)
    expect(received).toEqual(expected)
    value = '     0'
    received = hasNumber(value)
    expect(received).toEqual(expected)
  })
})
