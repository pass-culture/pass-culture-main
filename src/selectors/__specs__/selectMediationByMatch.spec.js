import selectMediationByRouterMatch from '../selectMediationByRouterMatch'

describe('src | selectors | selectMediationByRouterMatch', () => {
  it('should return mediation when mediationId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [],
      },
    }
    const match = {
      params: {
        mediationId: 'AE',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return mediation when bookingId in match resolves mediation', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'BF', mediationId: 'AE' }],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [{ id: 'AE' }],
      },
    }
    const match = {
      params: {
        bookingId: 'BF',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return mediation when favoriteId in match resolves mediation', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [{ id: 'BF', mediationId: 'AE' }],
        mediations: [{ id: 'AE' }],
        offers: [],
      },
    }
    const match = {
      params: {
        bookingId: 'AA',
        favoriteId: 'BF',
        mediationId: 'AE',
      },
    }

    // when
    const result = selectMediationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})
