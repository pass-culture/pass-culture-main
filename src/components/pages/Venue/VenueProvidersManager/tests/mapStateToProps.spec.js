import { selectCurrentUser } from 'with-login'

import mapStateToProps from '../mapStateToProps'

describe('src | components | pages | Venue | VenueProvidersManager', () => {
  describe('mapStateToProps', () => {
    it('should return an object with props', () => {
      // given
      const currentUserUUID = 'BABA'
      selectCurrentUser.currentUserUUID = currentUserUUID
      const state = {
        data: {
          providers: [
            { id: 'AF', localClass: 'a' },
            { id: 'AG', localClass: 'b' },
          ],
          venueProviders: [{ id: 'EE' }],
          users: [{ currentUserUUID, id: 'RR' }],
        },
        form: {
          venueProvider: {
            providerId: 'AG',
          },
        },
      }
      const props = {
        venue: { id: 'AE' },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toEqual({
        currentUser: {
          currentUserUUID: 'BABA',
          id: 'RR',
        },
        provider: { id: 'AG', localClass: 'b' },
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
        venueProvider: {
          venueId: 'AE',
        },
        venueProviders: [],
      })
    })
  })
})
