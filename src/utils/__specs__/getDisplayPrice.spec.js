import getDisplayPrice, { priceIsDefined } from '../getDisplayPrice'

const RIGHTWARDS_ARROW = '\u2192'
const NO_BREAK_SPACE = '\u00A0'

describe('src | helper | getDisplayPrice', () => {
  describe('priceIsDefined', () => {
    it('returns false', () => {
      let value = null
      let result = priceIsDefined(value)
      expect(result).toBe(false)

      value = 'null'
      result = priceIsDefined(value)
      expect(result).toBe(false)

      value = undefined
      result = priceIsDefined(value)
      expect(result).toBe(false)

      value = new Error()
      result = priceIsDefined(value)
      expect(result).toBe(false)
    })

    it('returns true', () => {
      let value = 0
      let result = priceIsDefined(value)
      expect(result).toBe(true)

      value = '0'
      result = priceIsDefined(value)
      expect(result).toBe(true)

      value = ['this is not a price']
      result = priceIsDefined(value)
      expect(result).toBe(true)

      value = false
      result = priceIsDefined(value)
      expect(result).toBe(true)

      value = { prop: 'this is not a price' }
      result = priceIsDefined(value)
      expect(result).toBe(true)
    })
  })

  describe('getDisplayPrice', () => {
    it('should return an empty string if empty array of numbers', () => {
      // when
      const result = getDisplayPrice([])

      // then
      expect(result).toBe('')
    })

    describe('with valid values', () => {
      it('should return simple value when one price is given', () => {
        // given
        const value = 15.1
        const freeValue = 'Gratuit'

        // when
        const result = getDisplayPrice(value, freeValue)

        // then
        expect(result).toBe(`15,1${NO_BREAK_SPACE}€`)
      })

      it('should return free value if defined and price equals 0', () => {
        // given
        const value = [0]
        const freeValue = 'Gratuit'

        // when
        const result = getDisplayPrice(value, freeValue)

        // then
        expect(result).toBe(freeValue)
      })

      it('should use Euro as default currency', () => {
        // given
        const value = [18.2]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toBe(`18,2${NO_BREAK_SPACE}€`)
      })

      it('should return value with currency from array', () => {
        // given
        const priceRange = [6, 12]

        // when
        const result = getDisplayPrice(priceRange)

        // then
        expect(result).toBe(`6 ${RIGHTWARDS_ARROW} 12${NO_BREAK_SPACE}€`)
      })

      it('should use comma as floating point', () => {
        // given
        const value = [1.33, 6.78]
        const freeValue = 'Gratuit'

        // when
        const result = getDisplayPrice(value, freeValue)

        // then
        expect(result).toBe(`1,33 ${RIGHTWARDS_ARROW} 6,78${NO_BREAK_SPACE}€`)
      })

      it('should not preserve comma when round value', () => {
        // given
        const value = [5.0]

        // when
        const result = getDisplayPrice(value)

        // then
        expect(result).toBe(`5${NO_BREAK_SPACE}€`)
      })

      describe('when the only price possible is 0', () => {
        it('should return Gratuit', () => {
          // given
          const value = [0]
          const freeValue = 'Gratuit'

          // when
          const result = getDisplayPrice(value, freeValue)

          // then
          expect(result).toBe(freeValue)
        })
      })
    })
  })
})
