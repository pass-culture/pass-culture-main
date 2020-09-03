import { mapDispatchToProps, mapStateToProps, mergeProps } from '../OfferItemContainer'

import state from '../../../../utils/mocks/state'

describe('src | components | pages | OfferItemContainer', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {}
  })

  describe('mapStateToProps', () => {
    let ownProps

    beforeEach(() => {
      ownProps = {
        offer: {
          offerId: 'UU',
          productId: 'LY',
          availabilityMessage: 'Encore 10 stocks restant',
          venueId: 'DA',
          type: 'ThingType.JEUX_VIDEO',
        },
        stocks: [{}],
      }
    })

    it('should return the value stocks', () => {
      // when

      const result = mapStateToProps(state, ownProps)
      const expected = []

      // then
      expect(result.stocks).toStrictEqual(expected)
    })

    it('should return the value of availabilityMessage', () => {
      // when
      const result = mapStateToProps(state, ownProps)
      const expected = 'Encore 10 stocks restant'

      // then
      expect(result.availabilityMessage).toStrictEqual(expected)
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
    it('should return an object containing functions to pass to component', () => {
      // when
      const result = mapDispatchToProps(dispatch, props)

      // then
      expect(result).toStrictEqual({
        updateOffer: expect.any(Function),
      })
    })

    describe('createVenueProvider', () => {
      it('should create a venue provider using API', () => {
        // given
        const functions = mapDispatchToProps(dispatch, props)

        const expectedParams = {
          config: {
            apiPath: '/offers/654FRT',
            body: { isActive: false },
            isMergingDatum: true,
            isMutaginArray: false,
            isMutatingDatum: true,
            method: 'PATCH',
            normalizer: {
              mediations: 'mediations',
              product: { normalizer: { offers: 'offers' }, stateKey: 'products' },
              stocks: 'stocks',
              venue: {
                normalizer: { managingOfferer: 'offerers' },
                stateKey: 'venues',
              },
            },
          },
          type: 'REQUEST_DATA_PATCH_/OFFERS/654FRT',
        }

        const offerId = '654FRT'
        const isActive = false

        // when
        functions.updateOffer(offerId, isActive)

        // then
        expect(dispatch).toHaveBeenCalledWith(expectedParams)
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {
        updateOffer: () => {},
      }
      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        match: ownProps.match,
        trackActivateOffer: expect.any(Function),
        trackDeactivateOffer: expect.any(Function),
        updateOffer: expect.any(Function),
      })
    })

    it('should map a tracking event for activate an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackActivateOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'activateOffer',
        name: 'RTgfd67',
      })
    })

    it('should map a tracking event for deactivate an offer', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackDeactivateOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'deactivateOffer',
        name: 'RTgfd67',
      })
    })
  })
})
