import { isWalletValid } from '../userSelector'

describe('isWalletValid', () => {
  it('returns true when the wallet is still valid', () => {
    // given
    const state = {
      currentUser: {
        wallet_date_created: '2019-02-01T09:00:00.000000Z',
        deposit_expiration_date: '2100-02-01T09:00:00.000000Z',
      },
    }

    // when
    const result = isWalletValid(state)

    // then
    expect(result).toStrictEqual(true)
  })

  it('returns false when the wallet is not valid anymore', () => {
    // given
    const state = {
      currentUser: {
        wallet_date_created: '2019-02-01T09:00:00.000000Z',
        deposit_expiration_date: '2021-02-01T09:00:00.000000Z',
      },
    }

    // when
    const result = isWalletValid(state)

    // then
    expect(result).toStrictEqual(false)
  })

  it('returns false when no wallet', () => {
    // given
    const state = {
      currentUser: {
        wallet_date_created: null,
        deposit_expiration_date: null,
      },
    }

    // when
    const result = isWalletValid(state)

    // then
    expect(result).toStrictEqual(false)
  })
})
