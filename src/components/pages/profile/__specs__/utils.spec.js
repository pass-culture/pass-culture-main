import getAvailableBalanceByType from '../utils'

describe('src | components | pages | profile | utils', () => {
  describe('getAvailableBalanceByType', () => {
    it('returns wallet balance if lower than max minus actual', () => {
      // given
      const wallet = 100
      const expense = { actual: 0, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toStrictEqual('100')
    })

    it('returns max minus actual if lower than wallet balance', () => {
      // given
      const wallet = 400
      const expense = { actual: 90, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toStrictEqual('110')
    })

    it('returns a balance with a maximum of two decimals when has decimal figures', () => {
      // given
      const wallet = 231.38
      const expense = { actual: 154.82, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toBe('45.18')
    })

    it('returns exactly two decimals when balance has one decimal figure', () => {
      // given
      const wallet = 231.38
      const expense = { actual: 154.8, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toBe('45.20')
    })
  })
})
