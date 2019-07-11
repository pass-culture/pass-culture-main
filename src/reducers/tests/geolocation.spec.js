import geolocation, {
  setGeolocationPosition,
  setGeolocationWatchId,
  SET_GEOLOCATION_POSITION,
  SET_GEOLOCATION_WATCH_ID,
} from '../geolocation'

// geolocation = reducer
describe('src | reducers | geolocation  ', () => {
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = geolocation(undefined, action)
    const expected = {
      latitude: null,
      longitude: null,
      watchId: null,
    }

    // then
    expect(updatedState).toStrictEqual(expected)
  })

  it('should set state when action is SET_GEOLOCATION_POSITION ', () => {
    // given
    const state = {}
    const action = {
      latitude: 1.1,
      longitude: 2.2,
      type: SET_GEOLOCATION_POSITION,
    }

    // when
    const updatedState = geolocation(state, action)
    const expected = {
      latitude: 1.1,
      longitude: 2.2,
    }

    // then
    expect(updatedState).toStrictEqual(expected)
  })

  it('should set state when action is SET_GEOLOCATION_WATCH_ID ', () => {
    // given
    const state = {}
    const action = {
      type: SET_GEOLOCATION_WATCH_ID,
      watchId: 1,
    }

    // when
    const updatedState = geolocation(state, action)
    const expected = { watchId: 1 }

    // then
    expect(updatedState).toStrictEqual(expected)
  })
})

describe('src | reducers | action | setGeolocationPosition', () => {
  it('should return correct action type', () => {
    // given
    const data = {
      latitude: 1.1,
      longitude: 2.2,
    }

    // when
    const action = setGeolocationPosition(data)
    const expected = {
      latitude: 1.1,
      longitude: 2.2,
      type: 'SET_GEOLOCATION_POSITION',
    }

    // then
    expect(action).toMatchObject(expected)
  })
})

describe('src | reducers | action | setGeolocationWatchId', () => {
  it('should return correct action type', () => {
    // when
    const action = setGeolocationWatchId(1)
    const expected = {
      type: SET_GEOLOCATION_WATCH_ID,
      watchId: 1,
    }

    // then
    expect(action).toMatchObject(expected)
  })
})
