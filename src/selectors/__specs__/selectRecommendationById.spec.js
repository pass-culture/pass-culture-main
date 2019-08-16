import selectRecommendationById from '../selectRecommendationById'

describe('src | selectors | selectRecommendationById', () => {
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
