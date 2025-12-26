import { normalizeRequestBodyProps } from '../normalizeRequestBodyProps'

describe('normalizeRequestBodyProps', () => {
  it('should normalize the request body properties', () => {
    const input = {
      undefinedProp: undefined,
      nullProp: null,
      emptyStringProp: '',
      whitespaceStringProp: '   ',
      stringProp: '  hello  ',
      numberProp: 123,
      booleanProp: true,
      arrayProp: [1, 2],
      objectProp: { x: 1 },
    }

    const result = normalizeRequestBodyProps(input)

    expect(result).toEqual({
      nullProp: null,
      emptyStringProp: null,
      whitespaceStringProp: null,
      stringProp: 'hello',
      numberProp: 123,
      booleanProp: true,
      arrayProp: [1, 2],
      objectProp: { x: 1 },
    })
  })
})
