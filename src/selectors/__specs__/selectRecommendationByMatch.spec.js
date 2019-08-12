import selectRecommendationByRouterMatch from '../selectRecommendationByRouterMatch'

describe('src | selectors | selectRecommendationByRouterMatch', () => {
  it('should return recommendation when offerId in match', () => {
    // given
    const offerId = 'AE'
    const offer = { id: offerId }
    const recommendation = {
      id: 'AE',
      offerId,
    }
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [],
        offers: [offer],
        recommendations: [recommendation],
        stocks: [{ offerId }],
      },
    }
    const match = {
      params: {
        mediationId: 'vide',
        offerId,
      },
    }

    // when
    const result = selectRecommendationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(recommendation)
  })

  it('should return recommendation when offerId and mediationId in match', () => {
    // given
    const offerId = 'AE'
    const offer = { id: offerId }
    const mediationId = 'AE'
    const mediation = { id: mediationId }
    const recommendation = {
      id: 'AE',
      mediationId,
      offerId,
    }
    const state = {
      data: {
        bookings: [],
        favorites: [],
        mediations: [mediation],
        offers: [offer],
        recommendations: [recommendation],
        stocks: [{ offerId }],
      },
    }
    const match = {
      params: {
        mediationId,
        offerId,
      },
    }

    // when
    const result = selectRecommendationByRouterMatch(state, match)

    // then
    expect(result).toStrictEqual(recommendation)
  })
})
