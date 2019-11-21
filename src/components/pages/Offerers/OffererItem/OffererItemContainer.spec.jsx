import state from '../../../utils/mocks/state'
import { mapStateToProps } from '../OffererItem/OffererItemContainer'

describe('src | components | pages | Offerers | OffererItem | OffererItemContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {
        offerer: {
          id: 'BA',
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        physicalVenues: [],
        venues: [
          {
            address: null,
            bookingEmail: 'john.doe@test.com',
            city: null,
            comment: null,
            dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
            departementCode: null,
            id: 'DA',
            idAtProviders: null,
            isValidated: true,
            isVirtual: true,
            lastProviderId: null,
            latitude: 48.83638,
            longitude: 2.40027,
            managingOffererId: 'BA',
            modelName: 'Venue',
            name: 'Le Sous-sol (Offre numérique)',
            postalCode: null,
            siret: null,
            thumbCount: 0,
            validationToken: null,
          },
        ],
      }
      expect(result).toStrictEqual(expected)
    })
  })
})
