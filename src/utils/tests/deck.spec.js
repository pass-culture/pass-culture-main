import { isThereRecommendations } from '../deck'

describe('src | utils | deck | isThereRecommendations', () => {
  // FIXME Negation that return true
  describe('When ???', () => {
    it('should return true', () => {
      const currentRecommendation = {}
      const recommendations = {}
      const previousProps = {
        recommendations: {},
      }
      expect(
        isThereRecommendations(
          recommendations,
          previousProps,
          currentRecommendation
        )
      ).toEqual(true)
    })
  })
})
