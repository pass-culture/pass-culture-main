// jest --env=jsdom ./src/components/forms/validators/tests/validateMatchingFields --watch
import { strings } from '../strings'
import { validateMatchingFields } from '../validateMatchingFields'

describe('src | components | forms | validators | validateMatchingFields', () => {
  it('it expect to return undefined - main value is not a password', () => {
    // given
    const value = ''
    const expected = undefined
    let mainvalue = ''

    // when
    let result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)

    // given
    mainvalue = '       '

    // when
    result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)

    // given
    mainvalue = '1234'

    // when
    result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return default error - main value is a password, value is not valid', () => {
    // given
    const mainvalue = '#1234Hello12'
    const expected = strings.DEFAULT_REQUIRED_ERROR
    let value = ''

    // when
    let result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '      '

    // when
    result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return undefined - values are passwords and equals', () => {
    // given
    const expected = undefined
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello12'

    // when
    const result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return not matching error - values are passwords but are not equals', () => {
    // given
    const expected = strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello43'

    // when
    const result = validateMatchingFields(value, mainvalue)

    // then
    expect(result).toStrictEqual(expected)
  })
})
