import geolocation from '../geolocation'
import { SET_GEOLOCATION_POSITION, SET_GEOLOCATION_WATCH_ID } from '../../actions/geolocation'

describe('reducers | geolocation', () => {
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

  it('should set state when action is SET_GEOLOCATION_POSITION', () => {
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

  it('should set state when action is SET_GEOLOCATION_WATCH_ID', () => {
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
