import data from '../data'

describe('src | reducers | data  ', () => {
  beforeEach(() => {
    const state = {
      bookings: [],
      recommendations: [],
    }
  })

  it('should return the initial state by default', () => {
    // given
    const action = {}
    const expected = {
      bookings: [],
      recommendations: [],
      types: []
    }

    // when
    const updatedState = data(undefined, action)

    // then
    expect(updatedState).toEqual(expected)
  })
})
