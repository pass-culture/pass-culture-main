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
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual(
      {
      "coordinates": {"latitude": null, "longitude": null},
       "tracking": {"trackEvent": expect.any(Function)},
        "userId": "Rt4R45ETEs"
        })
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
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual(
      {
      "coordinates": {"latitude": null, "longitude": null},
       "tracking": {"trackEvent": expect.any(Function)},
        "userId": "ANONYMOUS"
        })
    })
  })
})
