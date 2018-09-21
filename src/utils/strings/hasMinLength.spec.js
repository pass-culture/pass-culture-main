/* eslint no-console: 0, max-nested-callbacks: 0 */
import { hasMinLength } from './hasMinLength'

describe('src | utils | strings | hasMinLength', () => {
  it('return false', () => {
    const expected = false
    let value = false
    let received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = null
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = 1234
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = 0
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = undefined
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = null
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = []
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = {}
    received = hasMinLength(value)
    expect(received).toEqual(expected)
  })
  it('return true', () => {
    const expected = true
    let value = ''
    let received = hasMinLength(value, 0)
    expect(received).toEqual(expected)
    value = '     a'
    received = hasMinLength(value, 4)
    expect(received).toEqual(expected)
    value = 'string'
    received = hasMinLength(value, 6)
    expect(received).toEqual(expected)
  })
  it('return false because has no minimum defined', () => {
    const expected = false
    let value = ''
    let received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = '     a'
    received = hasMinLength(value)
    expect(received).toEqual(expected)
    value = 'a string'
    received = hasMinLength(value)
    expect(received).toEqual(expected)
  })
})
