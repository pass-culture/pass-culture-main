import { trimStringsInObject } from 'utils/trimStringsInObject'

describe('trimStringsInObject', () => {
  it('should gives the same object but with string blank spaces trimmed', () => {
    const fn = () => {}
    const date = new Date()
    const symbol = Symbol('foo')
    class TestClass {}

    const objectToBeTrimmed = {
      one: ' one', // needs to be trimmed
      two: 2,
      three: true,
      four: fn,
      five: date,
      six: 'six   ', // needs to be trimmed
      seven: symbol,
      eigth: BigInt(8),
      nine: {
        ten: '  ten ', // needs to be trimmed
        eleven: fn,
        twelve: date,
        thirteen: {
          fourteen: ' 14  ', // needs to be trimmed
          fiveteen: TestClass,
        },
      },
    }

    expect(trimStringsInObject(objectToBeTrimmed)).toStrictEqual({
      one: 'one', // trimmed
      two: 2,
      three: true,
      four: fn,
      five: date,
      six: 'six', // trimmed
      seven: symbol,
      eigth: BigInt(8),
      nine: {
        ten: 'ten', // trimmed
        eleven: fn,
        twelve: date,
        thirteen: {
          fourteen: '14', // trimmed
          fiveteen: TestClass,
        },
      },
    })
  })
})
