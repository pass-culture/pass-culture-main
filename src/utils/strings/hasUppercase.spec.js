/* eslint no-console: 0, max-nested-callbacks: 0 */
import { hasUppercase } from './hasUppercase'

describe('src | utils | strings | hasUppercase', () => {
  it('return false', () => {
    const expected = false
    let value = ''
    let received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = false
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = null
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = 1234
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = 0
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = undefined
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = null
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = []
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = {}
    received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = '      '
    received = hasUppercase(value)
    expect(received).toEqual(expected)
  })
  it('return true', () => {
    const expected = true
    let value = 'A'
    let received = hasUppercase(value)
    expect(received).toEqual(expected)
    value = '     A'
    received = hasUppercase(value)
    expect(received).toEqual(expected)
  })
})
