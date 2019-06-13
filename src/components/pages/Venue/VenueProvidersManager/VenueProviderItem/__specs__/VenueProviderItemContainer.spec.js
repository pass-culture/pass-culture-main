import { mapStateToProps } from '../VenueProviderItemContainer'
import state from '../../../../../utils/mocks/state'

describe('src | components | pages | Venue | VenueProvidersManager | VenueProviderContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with the right props', () => {
      // given
      const props = {
        venueProvider: {
          providerId: 123
        }
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toEqual({
        events: [],
        things: [{
          lastProviderId: 123
        }]
      })
    })
  })
})
