import { bookingNormalizer } from '../../../../utils/normalizers'
import { mapDispatchToProps, mapStateToProps, mergeProps } from '../BookingContainer'

jest.mock('../../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual(
    '../../../../utils/fetch-normalize-data/reducers/data/actionCreators'
  )

  return {
    requestData: _requestData,
  }
})

describe('src | components | layout | Booking | BookingContainer', () => {
  let state
  let match

  let offerId = 'AAA'
  let stockId = 'AE'

  let booking
  let offer

  beforeEach(() => {
    booking = {
      id: 'AAA',
      isCancelled: false,
      isUsed: false,
      stock: {
        quantity: 10,
        bookingLimitDatetime: '2018-11-27T23:59:56.790000Z',
        bookingRecapSent: null,
        dateModified: '2018-10-29T09:44:38.649450Z',
        dateModifiedAtLastProvider: '2018-10-29T09:44:38.649416Z',
        endDatetime: '2018-11-30T22:42:56.790000Z',
        groupSize: 1,
        id: stockId,
        idAtProviders: null,
        isSoftDeleted: false,
        lastProviderId: null,
        modelName: 'Stock',
        offerId,
        price: 10,
      },
    }
    offer = {
      bookingEmail: null,
      dateCreated: '2018-10-29T09:44:38.216817Z',
      dateModifiedAtLastProvider: '2018-10-29T09:44:38.216792Z',
      id: offerId,
      idAtProviders: null,
      isActive: true,
      isEvent: true,
      lastProviderId: null,
      modelName: 'Offer',
      product: {
        accessibility: '\u0000',
        ageMax: null,
        ageMin: null,
        conditions: null,
        dateModifiedAtLastProvider: '2018-10-29T09:44:38.012002Z',
        description: null,
        durationMinutes: 60,
        extraData: null,
        id: 'AE',
        idAtProviders: null,
        isNational: false,
        lastProviderId: null,
        mediaUrls: [],
        modelName: 'Event',
        name: 'Rencontre avec Franck Lepage',
        thumbCount: 1,
        type: 'EventType.CONFERENCE_DEBAT_DEDICACE',
      },
      productId: 'AE',
      venue: {
        address: '1 BD POISSONNIERE',
        bic: null,
        bookingEmail: 'fake@email.com',
        city: 'Paris',
        comment: null,
        dateModifiedAtLastProvider: '2018-10-29T09:44:37.451422Z',
        departementCode: '75',
        iban: null,
        id: 'AE',
        idAtProviders: null,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.87067,
        longitude: 2.3478,
        managingOffererId: 'AE',
        modelName: 'Venue',
        name: 'LE GRAND REX PARIS',
        postalCode: '75002',
        siret: '50763357600016',
        thumbCount: 0,
      },
      venueId: 'AE',
    }
    state = {
      data: {
        bookings: [booking],
        favorites: [],
        mediations: [],
        offers: [offer],
        stocks: [],
      },
      geolocation: {
        latitude: 48.8637404,
        longitude: 2.3374129,
      },
    }

    match = {
      params: {
        bookingId: 'AAA',
        mediationId: 'AAA',
        offerId,
      },
    }
  })

  describe('mapStateToProps', () => {
    describe('isEvent', () => {
      it('should return the matching booking', () => {
        // given
        const ownProps = {
          match,
        }

        // when
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result).toStrictEqual({
          bookables: [],
          offer: state.data.offers[0],
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('handleSubmit', () => {
      it('should call dispatch with request data', () => {
        // given
        const dispatch = jest.fn()
        const payload = {
          bookables: [],
          date: '2019-09-19T22:00:00.000Z',
          isDuo: true,
          price: 27,
          quantity: 2,
          stockId: 'BM',
          time: 'BM',
        }
        const handleRequestFail = jest.fn()
        const handleRequestSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch).handleSubmit(payload, handleRequestFail, handleRequestSuccess)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/bookings',
            body: {
              bookables: [],
              date: '2019-09-19T22:00:00.000Z',
              isDuo: true,
              price: 27,
              stockId: 'BM',
              time: 'BM',
              quantity: 2,
            },
            handleFail: handleRequestFail,
            handleSuccess: handleRequestSuccess,
            method: 'POST',
            name: 'booking',
            normalizer: bookingNormalizer,
          },
          type: 'REQUEST_DATA_POST_/BOOKINGS',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
      // given
      const stateProps = {
        offer: {
          id: 'B4',
        },
      }
      const dispatchProps = {
        handleSubmit: () => {},
      }
      const ownProps = {
        history: {
          location: {
            pathname: '/reservations/details/AE',
          },
        },
        match: {
          params: {
            bookings: 'AE',
          },
        },
      }
      // when
      const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

      // then
      expect(mergedProps).toStrictEqual({
        offer: { id: 'B4' },
        handleSubmit: expect.any(Function),
        history: {
          location: {
            pathname: '/reservations/details/AE',
          },
        },
        match: {
          params: {
            bookings: 'AE',
          },
        },
        trackBookingSuccess: expect.any(Function),
        trackBookOfferClickFromHomepage: expect.any(Function),
        trackBookOfferSuccessFromHomepage: expect.any(Function),
      })
    })

    it('should map a tracking event for booking an offer with root path url', () => {
      // given
      const stateProps = {
        offer: {
          id: 'B4',
        },
      }
      const ownProps = {
        history: {
          location: {
            pathname: '/reservations/details/AE',
          },
        },
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackBookingSuccess()

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'RESERVATIONS - bookingOffer',
        name: 'B4',
      })
    })
  })
})
