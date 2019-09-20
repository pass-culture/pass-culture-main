import * as reduxSagaData from 'redux-saga-data'

import { mapDispatchToProps, mapStateToProps, mergeProps } from '../BookingContainer'
import { bookingNormalizer } from '../../../../utils/normalizers'

describe('src | components | layout | Booking | BookingContainer', () => {
  let state
  let match

  let offerId = 'AAA'
  let stockId = 'AE'

  let booking
  let recommendation
  let offer

  beforeEach(() => {
    booking = {
      id: 'AAA',
      isCancelled: false,
      isUsed: false,
      stock: {
        available: 10,
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
    recommendation = {
      id: 'AAA',
      offerId,
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
        firstThumbDominantColor: [0, 0, 0],
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
        firstThumbDominantColor: null,
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
        recommendations: [recommendation],
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
      it('should return the matching booking given the recommendation', () => {
        // given
        const ownProps = {
          match,
        }

        // when
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result).toStrictEqual({
          bookables: [],
          booking: state.data.bookings[0],
          offer: state.data.offers[0],
          recommendation: state.data.recommendations[0],
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('handleSubmit', () => {
      it('should call dispatch with request data', () => {
        // given
        const dispatch = jest.fn()
        const formValues = {
          bookables: [],
          date: '2019-09-19T22:00:00.000Z',
          price: 27,
          recommendationId: 'NQ',
          stockId: 'BM',
          time: 'BM',
        }
        const handleRequestFail = jest.fn()
        const handleRequestSuccess = jest.fn()
        jest.spyOn(reduxSagaData, 'requestData')

        // when
        mapDispatchToProps(dispatch).handleSubmit(
          formValues,
          handleRequestFail,
          handleRequestSuccess
        )

        // then
        expect(reduxSagaData.requestData).toHaveBeenCalledWith({
          apiPath: '/bookings',
          body: {
            bookables: [],
            date: '2019-09-19T22:00:00.000Z',
            price: 27,
            recommendationId: 'NQ',
            stockId: 'BM',
            time: 'BM',
            quantity: 1,
          },
          handleFail: handleRequestFail,
          handleSuccess: handleRequestSuccess,
          method: 'POST',
          name: 'booking',
          normalizer: bookingNormalizer,
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
        match: {
          params: {
            bookings: 'AE',
          },
        },
        trackBookingSuccess: expect.any(Function),
      })
    })

    it('should map a tracking event for booking an offer', () => {
      // given
      const stateProps = {
        offer: {
          id: 'B4',
        },
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackBookingSuccess()

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'bookingOffer',
        name: 'B4',
      })
    })
  })
})
