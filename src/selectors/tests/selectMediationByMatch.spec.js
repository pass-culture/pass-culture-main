import selectMediationByMatch from '../selectMediationByMatch'

describe('src | selectors | selectMediationByMatch', () => {
  it('should return mediation when mediationId in match', () => {
    // given
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [],
        recommendations: [],
      },
    }
    const match = {
      params: {
        mediationId: 'AE',
      },
    }

    // when
    const result = selectMediationByMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })

  it('should return mediation when bookingId in match resolves mediation via recommendation', () => {
    // given
    const state = {
      data: {
        bookings: [{ id: 'BF', recommendationId: 'BF' }],
        favorites: [],
        mediations: [{ id: 'AE' }],
        offers: [{ id: 'AE' }],
        recommendations: [{ id: 'BF', mediationId: 'AE', offerId: 'AE' }],
      },
    }
    const match = {
      params: {
        bookingId: 'BF',
      },
    }

    // when
    const result = selectMediationByMatch(state, match)

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
        recommendations: [],
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
    const result = selectMediationByMatch(state, match)

    // then
    expect(result).toStrictEqual({ id: 'AE' })
  })
})
