import { mapDispatchToProps, mapStateToProps } from '../OffersContainer'

import state from '../../../utils/mocks/state'

describe('src | components | pages | Offers | OffersContainer', () => {
  let parse
  let ownProps
  let currentUser

  beforeEach(() => {
    parse = () => ({ lieu: 'DA', structure: 'BA' })
    currentUser = {}

    ownProps = {
      currentUser,
      handleOnActivateAllVenueOffersClick: jest.fn(),
      handleOnDeactivateAllVenueOffersClick: jest.fn(),
      handleSubmitRequestSuccess: jest.fn(),
      loadOffers: jest.fn(),
      loadTypes: jest.fn(),
      offers: [],
      query: {
        parse,
      },
      resetLoadedOffers: jest.fn(),
      venue: {},
    }
  })

  describe('mapStateToProps', () => {
    it('should return the value lastTrackerMoment', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = -Infinity

      // then
      expect(result.lastTrackerMoment).toStrictEqual(expected)
    })

    it('should return an object of prop offers', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = {
        bookingEmail: 'booking.email@test.com',
        dateCreated: '2019-03-07T10:39:23.560392Z',
        dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
        id: 'UU',
        idAtProviders: null,
        isActive: true,
        isEvent: false,
        isThing: true,
        lastProviderId: null,
        mediationsIds: ['H4'],
        modelName: 'Offer',
        productId: 'LY',
        stocksIds: ['MU'],
        venueId: 'DA',
      }

      // then
      expect(result.offers[0]).toStrictEqual(expected)
    })

    it('should return an object of prop offerer', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = {
        address: 'RUE DES SAPOTILLES',
        bic: 'QSDFGH8Z566',
        city: 'Cayenne',
        dateCreated: '2019-03-07T10:39:23.560414Z',
        dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
        iban: 'FR7630001007941234567890185',
        id: 'BA',
        idAtProviders: null,
        isActive: true,
        isValidated: true,
        lastProviderId: null,
        modelName: 'Offerer',
        nOffers: 5,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '222222233',
        thumbCount: 0,
        validationToken: null,
      }

      // then
      expect(result.offerer).toStrictEqual(expected)
    })

    it('should return an object of prop types', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = {
        appLabel: 'pass Culture : activation évènementielle',
        description: 'Activez votre pass Culture grâce à cette offre',
        id: 0,
        offlineOnly: true,
        onlineOnly: false,
        proLabel: 'pass Culture : activation évènementielle',
        sublabel: 'Activation',
        type: 'Event',
        value: 'EventType.ACTIVATION',
      }

      // then
      expect(result.types[0]).toStrictEqual(expected)
    })

    it('should return an object of prop venue', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = {
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
      }

      // then
      expect(result.venue).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('closeNotification', () => {
      it('enable to close notification', () => {
        // when
        mapDispatchToProps(dispatch).closeNotification()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          type: 'CLOSE_NOTIFICATION',
        })
      })
    })

    describe('handleOnActivateAllVenueOffersClick', () => {
      it('should activate all offers', () => {
        // given
        const venue = {
          id: 'AF',
        }

        // when
        mapDispatchToProps(dispatch).handleOnActivateAllVenueOffersClick(venue)()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/venues/AF/offers/activate',
            handleSuccess: undefined,
            method: 'PUT',
            stateKey: 'offers',
          },
          type: 'REQUEST_DATA_PUT_OFFERS',
        })
      })
    })

    describe('handleOnDeactivateAllVenueOffersClick', () => {
      it('should deactivate all offers', () => {
        // given
        const venue = {
          id: 'AF',
        }

        // when
        mapDispatchToProps(dispatch).handleOnDeactivateAllVenueOffersClick(venue)()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/venues/AF/offers/deactivate',
            handleSuccess: undefined,
            method: 'PUT',
            stateKey: 'offers',
          },
          type: 'REQUEST_DATA_PUT_OFFERS',
        })
      })
    })

    describe('loadOffers', () => {
      it('should load all offers', () => {
        // when
        mapDispatchToProps(dispatch).loadOffers()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            method: 'GET',
            normalizer: {
              mediations: 'mediations',
              product: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'products',
              },
              stocks: 'stocks',
              venue: {
                normalizer: {
                  managingOfferer: 'offerers',
                },
                stateKey: 'venues',
              },
            },
          },
          type: 'REQUEST_DATA_GET_UNDEFINED',
        })
      })
    })

    describe('loadTypes', () => {
      it('should load all types', () => {
        // when
        mapDispatchToProps(dispatch).loadTypes()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: { apiPath: '/types', method: 'GET' },
          type: 'REQUEST_DATA_GET_/TYPES',
        })
      })
    })

    describe('resetLoadedOffers', () => {
      it('should reset all loaded offers', () => {
        // when
        mapDispatchToProps(dispatch).resetLoadedOffers()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            offers: [],
          },
          type: 'ASSIGN_DATA',
        })
      })
    })
  })
})
