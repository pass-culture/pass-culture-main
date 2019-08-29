import selectPreviousRecommendation from '../selectPreviousRecommendation'

describe('src | components | pages | discovery | selectors | selectPreviousRecommendation', () => {
  it('should select the previous indexified recommendation', () => {
    // given
    const offerId = 'AE'
    const currentRecommendation = {
      productOrTutoIdentifier: 'foo',
      id: 'BF',
      offerId,
    }
    const previousRecommendation = {
      productOrTutoIdentifier: 'bar',
      offerId: 'BF',
    }
    const state = {
      data: {
        recommendations: [previousRecommendation, currentRecommendation],
      },
    }

    // when
    const result = selectPreviousRecommendation(state, offerId)

    // then
    const expected = {
      index: 0,
      path: `/decouverte/${previousRecommendation.offerId}/`,
      ...previousRecommendation,
    }
    expect(result).toStrictEqual(expected)
  })
})
