import { strings } from '../strings'
import { validateRequiredField } from '../validateRequiredField'

describe('src | components | forms | validators | validateRequiredField', () => {
  it('it expect to return default error with a string value', () => {
    // given
    const expected = strings.DEFAULT_REQUIRED_ERROR
    let value = ''

    // when
    let result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = '        '

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = false

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = undefined

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 0

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return OK (undefined) with not a string', () => {
    // given
    const expected = undefined
    let value = []

    // when
    let result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = []

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = {}

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = new Error()

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = true

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 1

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)
  })

  it('it expect to return OK (undefined) with a string', () => {
    // given
    const expected = undefined
    let value = 'a string from a text input'

    // when
    let result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)

    // given
    value = 'undefined'

    // when
    result = validateRequiredField(value)

    // then
    expect(result).toStrictEqual(expected)
  })
})
