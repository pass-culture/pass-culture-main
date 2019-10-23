import strings from '../strings'
import validatePasswordField from '../validatePasswordField'

describe('src | components | forms | validators | validatePasswordField', () => {
  it('it expect to return default error - not a string', () => {
    // given
    const expected = strings.PASSWORD_ERROR_MESSAGE
    let value = false

    // when
    let result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = null

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = undefined

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = []

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = {}

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = new Error()

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 1234

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return default error - not a valid string', () => {
    // given
    const expected = strings.PASSWORD_ERROR_MESSAGE
    let value = ''

    // when
    let result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '     '

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '12345679012'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '12345679012'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 'HelloHelloHe'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '############'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '-------------'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)
  })
  it('it expect to undefined - valid string', () => {
    // given
    const expected = undefined
    let value = '#1234Hello12'

    // when
    let result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 'Hello1234567'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = ' 1234Hello12'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '#1234 H ello'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '--1---H---l--'

    // when
    result = validatePasswordField(value)

    // then
    expect(result).toStrictEqual(expected)
  })
})
