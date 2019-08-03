import selectNextRecommendation from '../selectNextRecommendation'

describe('src | components | pages | discovery | selectors | selectNextRecommendation', () => {
  it('should select the next indexified recommendation', () => {
    // given
    const offerId = "AE"
    const currentRecommendation = {
      discoveryIdentifier: "foo",
      id: "BF",
      offerId
    }
    const nextRecommendation = {
      discoveryIdentifier: "bar",
      offerId: "BF"
    }
    const state = {
      data: {
        recommendations: [currentRecommendation, nextRecommendation]
      }
    }

    // when
    const result = selectNextRecommendation(state, offerId)

    // then
    const expected = {
      index: 1,
      path: `/decouverte/${nextRecommendation.offerId}/`,
      ...nextRecommendation
    }
    expect(result).toStrictEqual(expected)
  })
})
