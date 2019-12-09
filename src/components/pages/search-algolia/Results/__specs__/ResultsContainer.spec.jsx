import { mapStateToProps } from '../ResultsContainer'

describe('src | components | pages | search-algolia | Results | ResultsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        geolocation: {
          latitude: 48.866707485844245,
          longitude: 2.3348424546932867
        }
      }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        userLatitude: 48.866707485844245,
        userLongitude: 2.3348424546932867
      })
    })
  })
})
