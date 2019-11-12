import { selectReadRecommendations } from '../readRecommendationsSelectors'

describe('selectReadRecommendations', () => {
  it('should return read recommendations', () => {
    // given
    const state = {
      data: {
        readRecommendations: [{ id: 'AEY1' }]
      }
    }

    // when
    const result = selectReadRecommendations(state)

    // then
    expect(result).toStrictEqual([{ id: 'AEY1' }])
  })
})
