import {
  getDisplayPrice,
  defaultOutputPriceFormatter,
  priceIsDefined,
} from '../getDisplayPrice'

describe('priceIsDefined', () => {
  it('returns false', () => {
    const expected = false

    let value = null
    let result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = 'null'
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = undefined
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = new Error()
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)
  })

  it('returns true', () => {
    const expected = true

    let value = 0
    let result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = '0'
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = ['this is not a price']
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = false
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)

    value = { prop: 'this is not a price' }
    result = priceIsDefined(value)
    expect(result).toStrictEqual(expected)
  })
})

describe('defaultOutputPriceFormatter', () => {
  it('returns a string with not valid values', () => {
    const value = null
    const result = defaultOutputPriceFormatter(value, '€')
    const expected = '--'
    expect(result).toStrictEqual(expected)
  })

  it('returns a string with valid values with multi price', () => {
    const value = [12, 22]
    const result = defaultOutputPriceFormatter(value, '€')
    const expected = '12 \u2192 22 €'
    expect(result).toStrictEqual(expected)
  })

  it('returns a string with valid values with single price', () => {
    const value = [12]
    const result = defaultOutputPriceFormatter(value, '€')
    const expected = '12 €'
    expect(result).toStrictEqual(expected)
  })
})

describe('getDisplayPrice', () => {
  describe('with not valid values', () => {
    it('should return empty string if undefined || null', () => {
      const expected = ''
      let value
      let result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = null
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = 'null'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = new Error(null)
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
    })

    it('should return a empty string if not a number or array of numbers', () => {
      const expected = ''

      let value = false
      let result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = true
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = {}
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = []
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [null, undefined]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [true, {}]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [undefined]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
    })
  })

  describe('with valid values', () => {
    it('should return value with devise', () => {
      let value = 12
      let expected = '12 €'
      let result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = '12'
      expected = '12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = 12.42
      expected = '12,42 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = '12.42'
      expected = '12,42 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = '1222.00'
      expected = '1222 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
    })

    it('should return value with custom devise', () => {
      const value = '1222.00'
      const expected = '1222 poires'
      const result = getDisplayPrice(value, null, null, 'poires')
      expect(result).toStrictEqual(expected)
    })

    it('should return 0 €', () => {
      const expected = '0 €'
      let value = '0.00'
      let result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
      expect(result).toStrictEqual(expected)

      value = 0
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = '0'
      result = getDisplayPrice(value)
      value = [0, undefined]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [0, []]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [0, {}]
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
    })

    it('should return free value if defined and price equal 0', () => {
      const freeValue = 'Gratuit'
      let value = [0]
      let result = getDisplayPrice(value, freeValue)
      expect(result).toStrictEqual(freeValue)

      value = 0
      result = getDisplayPrice(value, freeValue)
      expect(result).toStrictEqual(freeValue)
    })

    it('should return value with devise from array', () => {
      // <!-- legacy
      let value = [6, 12]
      let expected = '6 \u2192 12 €'
      let result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['6', '12']
      expected = '6 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['6', '3', '49', '12']
      expected = '3 \u2192 49 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [12, 6]
      expected = '6 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [12, 0]
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = [0, 12]
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['0', '12']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['12', '0']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['12', '0.00']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)

      value = ['349', '12', '49', null, '28', '0.00', '3']
      expected = '0 \u2192 349 €'
      result = getDisplayPrice(value)
      expect(result).toStrictEqual(expected)
    })

    it('should return value with devise from array and not gratuit if defined', () => {
      // given
      const value = ['349', '12', '49', null, '28', '0.00', '3']

      // when
      const result = getDisplayPrice(value, 'Gratuit')

      // then
      const expected = '0 \u2192 349 €'
      expect(result).toStrictEqual(expected)
    })
  })

  describe('when getDisplayPrice is used in Discovery Card', () => {
    describe('when only one price that is 0', () => {
      it('it should return Gratuit', () => {
        // given
        const value = [0]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toStrictEqual('Gratuit')
      })
    })

    describe('when price is a float', () => {
      it('it should return floats with coma', () => {
        // given
        const value = [1.33, 6.78]

        // when
        const result = getDisplayPrice(value)

        // then
        const expected = '1,33 \u2192 6,78 €'
        expect(result).toStrictEqual(expected)
      })
    })

    describe('when price gots two decimals after coma that equals to zero', () => {
      it('it should return floats with coma', () => {
        // given
        const value = [5.0]

        // when
        const result = getDisplayPrice(value)

        // then
        const expected = '5 €'
        expect(result).toStrictEqual(expected)
      })
      it('it should return floats with coma', () => {
        // given
        const value = [12.42]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        const expected = '12,42 €'
        expect(result).toStrictEqual(expected)
      })
    })

    describe('when only one price without decimals', () => {
      it('should return value with devise', () => {
        // given
        const value = [5]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toStrictEqual('5 €')
      })
      it('should return value free value', () => {
        // given
        const value = [0]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toStrictEqual('Gratuit')
      })
    })

    describe('when one price is 0 and other is decimal', () => {
      it('it should return 0 and not gratuit if defined', () => {
        // given
        const value = [0, 4.34, 6.78]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toStrictEqual('0 \u2192 6,78 €')
      })
    })

    describe('with a specific formatter', () => {
      it('returns a formatted string', () => {
        // given
        const value = [12, 22]
        const euros = 'poires'
        const splitter = '\u0020this_is_the_splitter\u0020'

        // when
        const formatter = (prices, devise) => {
          const res = prices.join(splitter)
          return `${res}\u0020${devise}`
        }
        const result = getDisplayPrice(value, null, formatter, euros)

        // then
        const expected = `12${splitter}22\u0020${euros}`
        expect(result).toStrictEqual(expected)
      })
    })
  })
})
