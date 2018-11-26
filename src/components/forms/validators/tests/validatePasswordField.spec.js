// jest --env=jsdom ./src/components/forms/validators/tests/validatePasswordField --watch
import { strings } from '../strings'
import { validatePasswordField } from '../validatePasswordField'

describe('src | components | forms | validators | validatePasswordField', () => {
  it('it expect to return default error - not a string', () => {
    const expected = strings.PASSWORD_ERROR_MESSAGE
    let value = false
    let result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = null
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = undefined
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = []
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = {}
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = new Error()
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = 1234
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return default error - not a valid string', () => {
    const expected = strings.PASSWORD_ERROR_MESSAGE
    let value = ''
    let result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '     '
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '12345679012'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '12345679012'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = 'HelloHelloHe'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '############'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '-------------'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to undefined - valid string', () => {
    const expected = undefined
    let value = '#1234Hello12'
    let result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = 'Hello1234567'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = ' 1234Hello12'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '#1234 H ello'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
    value = '--1---H---l--'
    result = validatePasswordField(value)
    expect(result).toStrictEqual(expected)
  })
})
