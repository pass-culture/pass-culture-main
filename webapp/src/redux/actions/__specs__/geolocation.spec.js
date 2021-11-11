import {
  SET_GEOLOCATION_POSITION,
  SET_GEOLOCATION_WATCH_ID,
  setGeolocationPosition,
  setGeolocationWatchId
} from '../geolocation'

describe('actions | geolocation', () => {
  describe('setGeolocationPosition', () => {
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
        type: SET_GEOLOCATION_POSITION,
      }

      // then
      expect(action).toMatchObject(expected)
    })
  })
})

describe('setGeolocationWatchId', () => {
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
