// jest --env=jsdom ./src/components/forms/validators/tests/validateRequiredField --watch
import { strings } from '../strings'
import { validateRequiredField } from '../validateRequiredField'

describe('src | components | forms | validators | validateRequiredField', () => {
  it('it expect to return default error with a string value', () => {
    const expected = strings.DEFAULT_REQUIRED_ERROR
    let value = ''
    let result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = '        '
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = false
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = undefined
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = 0
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return OK (undefined) with not a string', () => {
    const expected = undefined
    let value = []
    let result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = []
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = {}
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = new Error()
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = true
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = 1
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
  })
  it('it expect to return OK (undefined) with a string', () => {
    const expected = undefined
    let value = 'a string from a text input'
    let result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
    value = 'undefined'
    result = validateRequiredField(value)
    expect(result).toStrictEqual(expected)
  })
})
