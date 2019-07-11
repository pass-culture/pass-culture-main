/* eslint no-console: 0, max-nested-callbacks: 0 */
import { isEmpty } from './isEmpty'

describe('src | utils | strings | isEmpty', () => {
  it('return false', () => {
    const expected = false
    let value = false
    let received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = 1234
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = 0
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = undefined
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = []
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = {}
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
  })
  it('return true', () => {
    const expected = true
    let value = '     '
    let received = isEmpty(value)
    expect(received).toStrictEqual(expected)
    value = ''
    received = isEmpty(value)
    expect(received).toStrictEqual(expected)
  })
})
