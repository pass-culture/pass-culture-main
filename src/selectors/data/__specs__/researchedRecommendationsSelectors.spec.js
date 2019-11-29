import { selectResearchedRecommendations } from '../researchedRecommendationsSelectors'

describe('researchedRecommendations', () => {
  it('should return researched recommendations', () => {
    // given
    const state = {
      data: {
        researchedRecommendations: [{ id: 'AEY1' }],
      },
    }

    // when
    const result = selectResearchedRecommendations(state)

    // then
    expect(result).toStrictEqual([{ id: 'AEY1' }])
  })
})
