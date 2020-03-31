import { mapStateToProps } from '../MatomoContainer'

describe('src | components | matomo | MatomoContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props when user logged in', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'Rt4R45ETEs',
            },
          ],
        },
        geolocation: {
          latitude: null,
          longitude: null,
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'Rt4R45ETEs' })
    })

    it('should return an object of props when user not logged in', () => {
      // given
      const state = {
        data: {
          users: [],
        },
        geolocation: {
          latitude: null,
          longitude: null,
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({ userId: 'ANONYMOUS' })
    })

    it('should map a tracking event when user activate geolocation', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'A6',
            },
          ],
        },
        geolocation: {
          longitude: 48.256756,
          latitude: 2.8796567,
          watchId: 1,
        },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      mapStateToProps(state, ownProps)

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'activatedGeolocation',
        name: 'A6',
      })
    })

    it('should  not map a tracking event when user does not activate geolocation', () => {
      // given
      const state = {
        data: {
          users: [
            {
              id: 'A6',
            },
          ],
        },
        geolocation: {
          longitude: null,
          latitude: null,
          watchId: 0,
        },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      mapStateToProps(state, ownProps)

      // then
      expect(ownProps.tracking.trackEvent).not.toHaveBeenCalledWith()
    })
  })
})
