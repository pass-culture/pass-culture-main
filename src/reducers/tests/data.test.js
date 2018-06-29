import data, { requestData } from '../data'

describe('src | reducers | data  ', () => {

  let state
  beforeEach(() => {
    state = {
      events: [],
      eventOccurences: [],
      mediations: [],
      occasions: [],
      offers: [],
      offerers: [],
      providers: [],
      things: [],
      types: [],
      venues: [],
      venueProviders: []
    }
  })

  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = data(undefined, action)

    // then
    expect(updatedState).toEqual(state)
  })

  describe('src |  actions', () => {

    describe('requestData', () => {
      it('should return correct action', () => {
        // given
        const method = 'POST'
        const path = 'http://fakeUrl.com'

        // when
        const action = requestData(method, path)
        const expected = {
          "config": {},
          "method": method,
          "path": path,
          type: "REQUEST_DATA_POST_HTTP://FAKEURL.COM"
        };

        // then
        expect(action).toMatchObject(expected);
      })
    })
  })
})
