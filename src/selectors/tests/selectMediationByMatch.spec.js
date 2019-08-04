import selectMediationByMatch from '../selectMediationByMatch'

describe('src | selectors | selectMediationByMatch', () => {
  it('should return mediation when mediationId in match', () => {
    // given
    const mediationId = 'AE'
    const mediation = { id: mediationId }
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [mediation],
        offers: [],
        recommendations: [],
      },
    }
    const match = {
      params: {
        mediationId,
      },
    }

    // when
    const result = selectMediationByMatch(state, match)

    // then
    expect(result).toStrictEqual(mediation)
  })

  it('should return mediation when bookingId in match resolves mediation via recommendation', () => {
    // given
    const offerId = 'AE'
    const offer = {
      id: offerId,
    }
    const mediationId = 'AE'
    const mediation = { id: mediationId }
    const bookingId = 'BF'
    const recommendationId = 'BF'
    const recommendation = { id: recommendationId, mediationId, offerId }
    const booking = { id: bookingId, recommendationId }
    const state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [mediation],
        offers: [offer],
        recommendations: [recommendation],
      },
    }
    const match = {
      params: {
        bookingId,
      },
    }

    // when
    const result = selectMediationByMatch(state, match)

    // then
    expect(result).toStrictEqual(mediation)
  })

  it('should return mediation when favoriteId in match resolves mediation', () => {
    // given
    const mediationId = 'AE'
    const mediation = { id: mediationId }
    const favoriteId = 'BF'
    const favorite = { id: favoriteId, mediationId }
    const state = {
      data: {
        bookings: [],
        favorites: [favorite],
        mediations: [mediation],
        offers: [],
        recommendations: [],
      },
    }
    const match = {
      params: {
        favoriteId,
      },
    }

    // when
    const result = selectMediationByMatch(state, match)

    // then
    expect(result).toStrictEqual(mediation)
  })
})
