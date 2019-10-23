import hasUppercase from './hasUppercase'

describe('src | utils | strings | hasUppercase', () => {
  it('return false', () => {
    const expected = false
    let value = ''
    let received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = false
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = 1234
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = 0
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = undefined
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = null
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = []
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = {}
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = '      '
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
  })

  it('return true', () => {
    const expected = true
    let value = 'A'
    let received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
    value = '     A'
    received = hasUppercase(value)
    expect(received).toStrictEqual(expected)
  })
})
