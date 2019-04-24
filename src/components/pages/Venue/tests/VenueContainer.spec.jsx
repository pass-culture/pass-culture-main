import React from 'react'
import { mapStateToProps } from '../VenueContainer'

describe('src | components | pages | Venue | VenueContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with props', () => {
      // given
      const state = {
        data: {
          offerers: [{ id: 1 }],
          userOfferers: [
            { offererId: 1, rights: 'RightsType.admin', userId: 1 },
          ],
          venues: [],
        },
        form: {
          venue: {
            geo: 40,
            latitude: 40,
            longitude: 40,
            name: 'Théâtre des bois',
            siret: 'ABC123',
          },
        },
        user: { email: 'john.doe@email.com' },
      }
      const props = {
        currentUser: { id: 1 },
        match: {
          params: {
            offererId: 1,
            venueId: 1,
          },
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toEqual({
        adminUserOfferer: {
          offererId: 1,
          rights: 'RightsType.admin',
          userId: 1,
        },
        formGeo: 40,
        formLatitude: 40,
        formLongitude: 40,
        formSiret: 'ABC123',
        name: 'Théâtre des bois',
        offerer: { id: 1 },
        venuePatch: {
          bookingEmail: 'john.doe@email.com',
          managingOffererId: 1,
        },
      })
    })
  })
})
