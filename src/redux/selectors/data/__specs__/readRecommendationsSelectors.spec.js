import { selectReadRecommendations } from '../readRecommendationsSelectors'

describe('selectReadRecommendations', () => {
  it('should return read recommendations when read recommendations exist', () => {
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

  it('should not return read recommendations when read recommendations not exist', () => {
    // given
    const state = {
      data: {
        readRecommendations: []
      }
    }

    // when
    const result = selectReadRecommendations(state)

    // then
    expect(result).toStrictEqual([])
  })
})
