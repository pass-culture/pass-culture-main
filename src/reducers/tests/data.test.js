import data from '../data'

describe('src | reducers | data  ', () => {

  let state
  beforeEach(() => {
    state = {
      bookings: [],
      recommendations: []
    }
  })

  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = data(undefined, action)

    console.log('updatedState', updatedState);

    // then
    expect(updatedState).toEqual(state)
  })
})
