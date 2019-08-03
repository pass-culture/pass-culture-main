import selectRecommendationByOfferIdAndMediationId from '../selectRecommendationByOfferIdAndMediationId'

describe('src | selectors | searchSelectors', () => {
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
    const result = selectRecommendationByOfferIdAndMediationId(
      state,
      offerId,
      mediationId
    )

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
    const result = selectRecommendationByOfferIdAndMediationId(
      state,
      offerId,
      mediationId
    )

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
    const result = selectRecommendationByOfferIdAndMediationId(
      state,
      offerId,
      mediationId
    )

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
    const result = selectRecommendationByOfferIdAndMediationId(
      state,
      offerId,
      mediationId
    )

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
    const result = selectRecommendationByOfferIdAndMediationId(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })
})
