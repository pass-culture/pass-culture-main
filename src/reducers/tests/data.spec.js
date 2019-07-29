import data from '../data'

describe('src | reducers | data ', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}
    const expected = {
      bookings: [],
      features: [],
      readRecommendations: [],
      recommendations: [],
      types: [],
      users: [],
    }

    // when
    const updatedState = data(undefined, action)

    // then
    expect(updatedState).toStrictEqual(expected)
  })
})
