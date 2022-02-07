/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

import state from 'components/utils/mocks/state'

import { mapStateToProps } from '../OffererItemContainer'

describe('src | components | pages | Offerers | OffererItem | OffererItemContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {
        offerer: {
          id: 'BA',
        },
        offers: [{}],
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        isVenueCreationAvailable: false,
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
            validationToken: null,
          },
        ],
      }
      expect(result).toStrictEqual(expected)
    })

    describe('isVenueCreationAvailable is based on feature flipping', () => {
      it('should mark offerer creation possible when API sirene is available', () => {
        // given
        const props = {
          offerer: {
            id: 'BA',
          },
        }
        const state = {
          features: {
            list: [
              {
                isActive: true,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isVenueCreationAvailable', true)
      })

      it('should prevent offerer creation when feature API sirene is not available', () => {
        // given
        const props = {
          offerer: {
            id: 'BA',
          },
        }
        const state = {
          features: {
            list: [
              {
                isActive: false,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isVenueCreationAvailable', false)
      })
    })
  })
})
