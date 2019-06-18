import {
  isDiscoveryStartupPathname,
  MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS,
} from '../utils'

describe('src | components | pages | discovery | tests | utils', () => {
  describe('MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS', () => {
    it('should be equals to 3 hours in milliseconds', () => {
      const expected = 3 * 60 * 60 * 1000
      expect(MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS).toEqual(
        expected
      )
    })
  })

  describe('isDiscoveryStartupPathname', () => {
    describe('return false', () => {
      it('when location is an array', () => {
        // given
        const value = []

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = false
        expect(result).toStrictEqual(expected)
      })

      it('when location is an object', () => {
        // given
        const value = {}

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = false
        expect(result).toStrictEqual(expected)
      })

      it('when location is null', () => {
        // given
        const value = null

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = false
        expect(result).toStrictEqual(expected)
      })

      it('when location is undefined', () => {
        // given
        const value = undefined

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = false
        expect(result).toStrictEqual(expected)
      })

      it('when location is location equals to /decouverte/{OfferID}/{MediationID}', () => {
        // given
        const value = undefined
        const result = isDiscoveryStartupPathname(value)

        const expected = false
        expect(result).toStrictEqual(expected)
      })

      it('when location is location equals to /search', () => {
        // given
        const value = undefined
        const result = isDiscoveryStartupPathname(value)

        const expected = false
        expect(result).toStrictEqual(expected)
      })
    })

    describe('return true', () => {
      it('when location equals /decouverte', () => {
        // given
        const value = '/decouverte'

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = true
        expect(result).toStrictEqual(expected)
      })
      it('when location equals /decouverte with a trailing slash', () => {
        // given
        const value = '/decouverte/'

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = true
        expect(result).toStrictEqual(expected)
      })

      it('when location equals /decouverte/tuto/fin', () => {
        // given
        const value = '/decouverte/tuto/fin'

        // when
        const result = isDiscoveryStartupPathname(value)

        // then
        const expected = true
        expect(result).toStrictEqual(expected)
      })

      it('when location equals /decouverte/tuto/fin with a trailing slash', () => {
        // given
        const value = '/decouverte/tuto/fin/'

        // then
        const result = isDiscoveryStartupPathname(value)

        // when
        const expected = true
        expect(result).toStrictEqual(expected)
      })
    })
  })
})
