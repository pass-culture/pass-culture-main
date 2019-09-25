import { mapStateToProps, mergeProps } from '../OfferContainer'
import state from '../../../utils/mocks/state'

describe('src | components | pages | Offer | Offer | OfferContainer ', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          offerId: 'UU',
        },
      },
      query: {
        translate: jest.fn(),
      },
      trackCreateOffer: jest.fn(),
      trackModifyOffer: jest.fn(),
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        formInitialValues: expect.any(Object),
        formOffererId: 'BA',
        formVenueId: 'DA',
        offer: {
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
        },
        offerer: expect.any(Object),
        offerers: expect.any(Object),
        product: expect.any(Object),
        providers: [],
        selectedOfferType: expect.any(Object),
        stocks: expect.any(Object),
        types: expect.any(Object),
        url: 'https://ilestencoretemps.fr/',
        venue: expect.any(Object),
        venues: expect.any(Object),
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {}
      const dispatchProps = {}
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
        trackCreateOffer: expect.any(Function),
        trackModifyOffer: expect.any(Function),
      })
    })

    it('should map a tracking event for creating a venue', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackCreateOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'createOffer',
        name: 'RTgfd67',
      })
    })

    it('should map a tracking event for updating a venue', () => {
      // given
      const stateProps = {}
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackModifyOffer('RTgfd67')

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'modifyOffer',
        name: 'RTgfd67',
      })
    })
  })
})
