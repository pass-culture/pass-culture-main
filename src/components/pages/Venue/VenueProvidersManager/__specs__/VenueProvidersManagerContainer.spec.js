import { mapStateToProps } from '../VenueProvidersManagerContainer'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  describe('mapStateToProps', () => {
    it('should return an object with props', () => {
      // given
      const state = {
        data: {
          providers: [
            {id: 'AF', localClass: 'a'},
            {id: 'AG', localClass: 'b'},
          ],
          venueProviders: [{id: 'EE'}],
        },
      }
      const props = {
        venue: {id: 'AE'},
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toEqual({
        providers: [
          {
            id: 'AF',
            localClass: 'a',
          },
          {
            id: 'AG',
            localClass: 'b',
          },
        ],
        venueProviders: [],
      })
    })
  })
})
