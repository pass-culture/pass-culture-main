import strings from '../strings'
import validateMatchingFields from '../validateMatchingFields'

describe('src | components | forms | validators | validateMatchingFields', () => {
  it('expect to return undefined - mainvalue is falsey', () => {
    // given
    const value = ''
    const mainvalue = ''
    // when
    const result = validateMatchingFields(value, mainvalue)
    // then
    const expected = undefined
    expect(result).toStrictEqual(expected)
  })

  it('expect to return default error - main value is a password, value is not valid', () => {
    // given
    const mainvalue = '#1234Hello12'
    const value = ''
    // when
    const result = validateMatchingFields(value, mainvalue)
    // then
    const expected = strings.DEFAULT_REQUIRED_ERROR
    expect(result).toStrictEqual(expected)
  })

  it('expect to return default error - main value is a password, value is not valid (changer le titre du test)', () => {
    // given
    const mainvalue = '#1234Hello12'
    const value = '      '
    // when
    const result = validateMatchingFields(value, mainvalue)
    // then
    const expected = strings.DEFAULT_REQUIRED_ERROR
    expect(result).toStrictEqual(expected)
  })

  it('expect to return undefined - values are passwords and equals', () => {
    // given
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello12'
    // when
    const result = validateMatchingFields(value, mainvalue)
    // then
    const expected = undefined
    expect(result).toStrictEqual(expected)
  })

  it('expect to return not matching error - values are passwords but are not equals', () => {
    // given
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello43'
    // when
    const result = validateMatchingFields(value, mainvalue)
    // then
    const expected = strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM
    expect(result).toStrictEqual(expected)
  })
})
