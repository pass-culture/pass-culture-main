import {
  selectRecommendationById,
  selectRecommendationByOfferIdAndMediationId,
  selectRecommendationByRouterMatch,
  selectRecommendations,
} from '../recommendationsSelectors'

describe('selectRecommendations', () => {
  it('should return recommendations', () => {
    // given
    const state = {
      data: {
        recommendations: [{ id: 'AEY1' }],
      },
    }

    // when
    const result = selectRecommendations(state)

    // then
    expect(result).toStrictEqual([{ id: 'AEY1' }])
  })
})

describe('selectRecommendationById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        recommendations: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectRecommendationById(state, 'wrong')

    // then
    expect(result).toBeUndefined()
  })

  it('should return recommendation matching id', () => {
    // given
    const state = {
      data: {
        recommendations: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectRecommendationById(state, 'bar')

    // then
    expect(result).toStrictEqual({ id: 'bar' })
    expect(result).toBe(state.data.recommendations[1])
  })
})

describe('selectRecommendationByOfferIdAndMediationId', () => {
  it('return undefined when mediationId and offerId are not defined', () => {
    // given
    const state = {
      data: {
        recommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = undefined
    const mediationId = undefined
    const result = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)

    // then
    expect(result).toBeUndefined()
  })

  it('return undefined when any recommantions is matching with offerId or mediationId', () => {
    // given
    const state = {
      data: {
        recommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'ZZZZ'
    const mediationId = '0000'
    const result = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)

    // then
    expect(result).toBeUndefined()
  })

  it('return undefined when recommendations are empties', () => {
    // given
    const state = {
      data: {
        recommendations: [],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '1234'
    const result = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)

    // then
    expect(result).toBeUndefined()
  })

  it('return recommendation with offerId AAAA when mediationId 5678', () => {
    // given
    const state = {
      data: {
        recommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '5678'
    const result = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })

  it('return recommendation with offerId BBBB when mediationId is 5678', () => {
    // given
    const state = {
      data: {
        recommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '5678'
    const result = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })
})

describe('selectRecommendationByRouterMatch', () => {
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
