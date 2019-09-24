import { getAvailableBalanceByType } from '../utils'

describe('src | components | pages | profile | utils', () => {
  describe('getAvailableBalanceByType', () => {
    it('returns a placeholder string if missing wallet balance', () => {
      // given
      const wallet = null
      const expense = { actual: 0, max: 0 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = '--'
      expect(result).toStrictEqual(expected)
    })

    it('returns a placeholder string if missing max', () => {
      // given
      const wallet = 0
      const expense = { actual: 0, max: null }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = '--'
      expect(result).toStrictEqual(expected)
    })

    it('returns a placeholder string if missing actual', () => {
      // given
      const wallet = 0
      const expense = { actual: null, max: 0 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = '--'
      expect(result).toStrictEqual(expected)
    })

    it('returns minimum values between wallet and expense', () => {
      // given
      const wallet = 0
      const expense = { actual: 0, max: 0 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = 0
      expect(result).toStrictEqual(expected)
    })

    it('returns wallet balance if lower than max - actual', () => {
      // given
      const wallet = 100
      const expense = { actual: 0, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = 100
      expect(result).toStrictEqual(expected)
    })

    it('returns max - actual if lower than wallet balance', () => {
      // given
      const wallet = 400
      const expense = { actual: 90, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      const expected = 110
      expect(result).toStrictEqual(expected)
    })

    it('should return only two decimals', () => {
      // given
      const wallet = 231.38
      const expense = { actual: 154.8, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toBe(45.2)
    })
  })
})
