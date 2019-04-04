import { getDisplayPrice } from '../getDisplayPrice'

describe('getDisplayPrice - format a value with devise', () => {
  describe('with not valid values', () => {
    it('should return empty string if undefined || null', () => {
      const expected = ''
      let value
      let result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = null
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = 'null'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = new Error(null)
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
    })
    it('should return a empty string if not a number or array of numbers', () => {
      const expected = ''
      let value = false
      let result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = true
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = {}
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = []
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [null, undefined]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [true, {}]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [undefined]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
    })
  })
  describe('with valid values', () => {
    it('should return value with devise', () => {
      let value = 12
      let expected = '12 €'
      let result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = '12'
      expected = '12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = 12.42
      expected = '12,42 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = '12.42'
      expected = '12,42 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = '1222.00'
      expected = '1222 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
    })
    it('should return value with custom devise', () => {
      const value = '1222.00'
      const expected = '1222 poires'
      const result = getDisplayPrice(value, null, 'poires')
      expect(result).toEqual(expected)
    })
    it('should return 0 €', () => {
      const expected = '0 €'
      let value = '0.00'
      let result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      expect(result).toEqual(expected)
      value = 0
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = '0'
      result = getDisplayPrice(value)
      value = [0, undefined]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [0, []]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [0, {}]
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
    })
    it('should return free value if defined and price equal 0', () => {
      const freeValue = 'Gratuit'
      let value = [0]
      let result = getDisplayPrice(value, freeValue)
      expect(result).toEqual(freeValue)
      value = 0
      result = getDisplayPrice(value, freeValue)
      expect(result).toEqual(freeValue)
    })
    it('should return value with devise from array', () => {
      // <!-- legacy
      let value = [6, 12]
      let expected = '6 \u2192 12 €'
      let result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['6', '12']
      expected = '6 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['6', '3', '49', '12']
      expected = '3 \u2192 49 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [12, 6]
      expected = '6 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [12, 0]
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = [0, 12]
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['0', '12']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['12', '0']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['12', '0.00']
      expected = '0 \u2192 12 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
      value = ['349', '12', '49', null, '28', '0.00', '3']
      expected = '0 \u2192 349 €'
      result = getDisplayPrice(value)
      expect(result).toEqual(expected)
    })
    it('should return value with devise from array and not gratuit if defined', () => {
      const value = ['349', '12', '49', null, '28', '0.00', '3']
      const expected = '0 \u2192 349 €'
      const result = getDisplayPrice(value, 'Gratuit')
      expect(result).toEqual(expected)
    })
  })
  describe('When getDisplayPrice is used in Discovery Card', () => {
    describe('when only one price that is 0', () => {
      it('it should return Gratuit', () => {
        // given
        const value = [0]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toEqual('Gratuit')
      })
    })

    describe('when price is a float', () => {
      it('it should return floats with coma', () => {
        // given
        const value = [1.33, 6.78]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toEqual('1,33 \u2192 6,78 €')
      })
    })

    describe('when price gots two decimals after coma that equals to zero', () => {
      it('it should return floats with coma', () => {
        // given
        const value = [5.0]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toEqual('5 €')
      })
      it('it should return floats with coma', () => {
        // given
        const value = [12.42]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toEqual('12,42 €')
      })
    })

    describe('when only one price without decimals', () => {
      it('should return value with devise', () => {
        // given
        const value = [5]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toEqual('5 €')
      })
      it('should return value free value', () => {
        // given
        const value = [0]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toEqual('Gratuit')
      })
    })

    describe('when one price is 0 and other is decimal', () => {
      it('it should return 0 and not gratuit if defined', () => {
        // given
        const value = [0, 4.34, 6.78]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        expect(result).toEqual('0 \u2192 6,78 €')
      })
    })
  })
})
