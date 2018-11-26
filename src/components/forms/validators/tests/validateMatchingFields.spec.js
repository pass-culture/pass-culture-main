// jest --env=jsdom ./src/components/forms/validators/tests/validateMatchingFields --watch
import { strings } from '../strings'
import { validateMatchingFields } from '../validateMatchingFields'

describe('src | components | forms | validators | validateMatchingFields', () => {
  it('it expect to return undefined - main value is not a password', () => {
    const value = ''
    const expected = undefined
    let mainvalue = ''
    let result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
    mainvalue = '       '
    result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
    mainvalue = '1234'
    result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return default error - main value is a password, value is not valid', () => {
    const mainvalue = '#1234Hello12'
    const expected = strings.DEFAULT_REQUIRED_ERROR
    let value = ''
    let result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
    value = '      '
    result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return undefined - values are passwords and equals', () => {
    const expected = undefined
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello12'
    const result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return not matching error - values are passwords but are not equals', () => {
    const expected = strings.PASSWORD_ERROR_IS_NOT_MATCHING_CONFIRM
    const value = '#1234Hello12'
    const mainvalue = '#1234Hello43'
    const result = validateMatchingFields(value, mainvalue)
    expect(result).toStrictEqual(expected)
  })
})
