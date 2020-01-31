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
      expect(result).toStrictEqual(100)
    })

    it('returns max minus actual if lower than wallet balance', () => {
      // given
      const wallet = 400
      const expense = { actual: 90, max: 200 }

      // then
      const result = getAvailableBalanceByType(wallet)(expense)

      // when
      expect(result).toStrictEqual(110)
    })
  })
})
