import selectIsUserAdmin from '../userSelectors'

describe('src | components | pages | Bookings | selectors | selectIsUserAdmin', () => {
  it('should return false when state contains no users', () => {
    // given
    const state = {
      data: {
        users: [],
      },
    }

    // when
    const result = selectIsUserAdmin(state)

    // then
    expect(result).toStrictEqual(false)
  })

  it('should return true when state contain an admin user', () => {
    // given
    const state = {
      data: {
        users: [
          {
            id: 'FA',
            isAdmin: true,
          },
        ],
      },
    }

    // when
    const result = selectIsUserAdmin(state)

    // then
    expect(result).toStrictEqual(true)
  })

  it('should return false when state contain no admin user', () => {
    // given
    const state = {
      data: {
        users: [
          {
            id: 'EF',
            isAdmin: false,
          },
        ],
      },
    }

    // when
    const result = selectIsUserAdmin(state)

    // then
    expect(result).toStrictEqual(false)
  })
})
