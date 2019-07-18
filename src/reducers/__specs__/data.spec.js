import data, { lastRecommendationsRequestTimestamp } from '../data'

describe('src | reducers | data', () => {
  describe('data()', () => {
    it('should return the initial state by default', () => {
      // given
      const action = {}

      // when
      const updatedState = data(undefined, action)

      // then
      const expected = {
        bookings: [],
        features: null,
        readRecommendations: [],
        recommendations: [],
        types: [],
        users: [],
      }
      expect(updatedState).toStrictEqual(expected)
    })
  })

  describe('lastRecommendationsRequestTimestamp()', () => {
    it('should return the date of now', () => {
      // given
      jest.spyOn(Date, 'now').mockImplementation(() => '31/05/1982')
      const state = 0
      const action = {
        type: 'SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP',
      }

      // when
      const lastRecommendations = lastRecommendationsRequestTimestamp(state, action)

      // then
      expect(lastRecommendations).toStrictEqual('31/05/1982')
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
      expect(lastRecommendations).toStrictEqual(state)
    })
  })
})
