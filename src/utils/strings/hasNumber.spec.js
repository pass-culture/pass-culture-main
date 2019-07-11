import { hasNumber } from './hasNumber'

describe('src | utils | strings | hasNumber', () => {
  it('return false', () => {
    const expected = false
    let value = ''
    let received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = false
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = 1234
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = 0
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = undefined
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = []
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = {}
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = '      '
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
  })

  it('return true', () => {
    const expected = true
    let value = '1'
    let received = hasNumber(value)
    expect(received).toStrictEqual(expected)
    value = '     0'
    received = hasNumber(value)
    expect(received).toStrictEqual(expected)
  })
})
