import getWalletValue from '../getWalletValue'

describe('src | utils | user | getWalletValue', () => {
  describe('user is valid', () => {
    it('returns a number value gt 0', () => {
      // given
      const user = { wallet_balance: 500 }

      // when
      const result = getWalletValue(user)

      // then
      expect(result).toStrictEqual(500)
    })

    it('returns a number eql 0', () => {
      const user = { wallet_balance: 0 }
      const result = getWalletValue(user)
      expect(result).toStrictEqual(0)
    })

    it('returns a number when user.wallet_balance < 0', () => {
      // given
      const user = { wallet_balance: -100 }

      // when
      const result = getWalletValue(user)

      // then
      expect(result).toStrictEqual(-100)
    })
  })

  describe('is not valid, returns a default string', () => {
    it('when user is null', () => {
      // given
      const user = null

      // when
      const result = getWalletValue(user)

      // then
      expect(result).toStrictEqual('--')
    })

    it('when user has no wallet balance', () => {
      // given
      const user = {}

      // when
      const result = getWalletValue(user)

      // then
      expect(result).toStrictEqual('--')
    })

    it('when user.wallet_balance is not a number', () => {
      // given
      const user = { wallet_balance: '0' }

      // when
      const result = getWalletValue(user)

      // then
      expect(result).toStrictEqual('--')
    })

    it('custom fallback', () => {
      // given
      const user = null
      const fallbackString = 'this is a placeholder'

      // when
      const result = getWalletValue(user, fallbackString)

      // then
      expect(result).toStrictEqual(fallbackString)
    })
  })
})
