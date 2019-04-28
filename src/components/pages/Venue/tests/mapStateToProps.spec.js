import mapStateToProps from '../mapStateToProps'

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
        query: {
          context: () => ({
            isCreatedEntity: true,
          }),
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
        offerer: { id: 1 },
        formInitialValues: {
          bookingEmail: 'john.doe@email.com',
          managingOffererId: 1,
        },
      })
    })
  })
})
