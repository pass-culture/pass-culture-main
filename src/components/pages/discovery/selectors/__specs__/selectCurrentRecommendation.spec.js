import selectCurrentRecommendation from '../selectCurrentRecommendation'

describe('src | components | pages | discovery | selectors | selectCurrentRecommendation', () => {
  let offerId
  let mediationId

  describe('when there is offerId and no mediationId', () => {
    it('should select the current recommendation corresponding to match params', () => {
      // given
      mediationId = 'FF'
      offerId = 'ARBA'
      const recommendation = {
        discoveryIdentifier: "foo",
        mediationId,
        offerId
      }
      const state = {
        data: {
          recommendations: [recommendation]
        }
      }

      // when
      const result = selectCurrentRecommendation(state, offerId, mediationId)

      // then
      const expected = {
        index: 0,
        ...recommendation
      }
      expect(result).toStrictEqual(expected)
    })
  })
})
