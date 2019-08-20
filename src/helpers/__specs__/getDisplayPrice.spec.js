import { getDisplayPrice, priceIsDefined } from '../getDisplayPrice'

describe('src | helper | getDisplayPrice', () => {
  describe('priceIsDefined', () => {
    it('returns false', () => {
      const expected = false

      let value = null
      let result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = 'null'
      result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = undefined
      result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = new Error()
      result = priceIsDefined(value)
      expect(result).toBe(expected)
    })

    it('returns true', () => {
      const expected = true

      let value = 0
      let result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = '0'
      result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = ['this is not a price']
      result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = false
      result = priceIsDefined(value)
      expect(result).toBe(expected)

      value = { prop: 'this is not a price' }
      result = priceIsDefined(value)
      expect(result).toBe(expected)
    })
  })

  describe('getDisplayPrice', () => {
    it('should return a empty string if empty array of numbers', () => {
      // When
      const result = getDisplayPrice([])

      // Then
      expect(result).toBe('')
    })

    describe('with valid values', () => {
      it('should return simple value when one price is given', () => {
        // Given
        let value = 15.1

        // When
        let result = getDisplayPrice(value, 'Gratuit')

        // Then
        expect(result).toBe('15,1 €')
      })

      it('should return free value if defined and price equals 0', () => {
        // Given
        const freeValue = 'Gratuit'
        let value = [0]

        // When
        let result = getDisplayPrice(value, freeValue)

        // Then
        expect(result).toBe(freeValue)
      })

      it('should use Euro as default currency', () => {
        // Given
        let value = [18.2]

        // When
        const result = getDisplayPrice(value)

        // Then
        expect(result).toBe('18,2 €')
      })

      it('should return value with currency from array', () => {
        // Given
        const priceRange = [6, 12]

        // When
        const result = getDisplayPrice(priceRange)

        // Then
        expect(result).toBe('6 \u2192 12 €')
      })

      it('should use comma as floating point', () => {
        // given
        const value = [1.33, 6.78]

        // when
        const result = getDisplayPrice(value, 'Gratuit')

        // then
        const expected = '1,33 \u2192 6,78 €'
        expect(result).toBe(expected)
      })

      it('should not preserve comma when round value', () => {
        // given
        const value = [5.0]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toBe('5 €')
      })

      describe('when the only price possible is 0', () => {
        it('should return Gratuit', () => {
          // given
          const value = [0]

          // when
          const result = getDisplayPrice(value, 'Gratuit')

          // then
          expect(result).toBe('Gratuit')
        })
      })
    })
  })
})
