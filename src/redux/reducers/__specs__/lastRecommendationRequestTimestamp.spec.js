import lastRecommendationsRequestTimestamp from '../lastRecommendationRequestTimestamp'

describe('reducers | lastRecommendationsRequestTimestamp', () => {
  it('should return the date of now', () => {
    // given
    jest.spyOn(global.Date, 'now').mockImplementation(() => '31/05/1982')
    const state = 0
    const action = {
      type: 'SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP',
    }

    // when
    const lastRecommendations = lastRecommendationsRequestTimestamp(state, action)

    // then
    expect(lastRecommendations).toBe('31/05/1982')
  })

  it('should return the initial state', () => {
    // given
    const state = 0
    const action = {
      type: '',
    }

    // when
    const lastRecommendations = lastRecommendationsRequestTimestamp(state, action)

    // then
    expect(lastRecommendations).toBe(state)
  })
})
