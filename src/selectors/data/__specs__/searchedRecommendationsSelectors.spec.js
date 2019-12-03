import { selectSearchedRecommendations } from '../searchedRecommendationsSelectors'

describe('searchedRecommendations', () => {
  it('should return searched recommendations', () => {
    // given
    const state = {
      data: {
        searchedRecommendations: [{ id: 'AEY1' }],
      },
    }

    // when
    const result = selectSearchedRecommendations(state)

    // then
    expect(result).toStrictEqual([{ id: 'AEY1' }])
  })
})
