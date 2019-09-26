import getWalletValue from '../getWalletValue'

describe('src | utils | user | getWalletValue', () => {
  it('returns a value with two decimals when wallet balance has two decimal digits', () => {
    // given
    const user = { wallet_balance: 476.98 }

    // when
    const result = getWalletValue(user)

    // then
    expect(result).toStrictEqual('476.98')
  })

  it('returns a value with two decimals when wallet balance has one decimal digits', () => {
    // given
    const user = { wallet_balance: 476.9 }

    // when
    const result = getWalletValue(user)

    // then
    expect(result).toStrictEqual('476.90')
  })

  it('returns a value with no decimals when wallet balance has no decimal digits', () => {
    // given
    const user = { wallet_balance: 476 }

    // when
    const result = getWalletValue(user)

    // then
    expect(result).toStrictEqual('476')
  })

  it('returns null if user undefined', () => {
    // given
    const user = undefined

    // when
    const result = getWalletValue(user)

    // then
    expect(result).not.toBeDefined()
  })
})
