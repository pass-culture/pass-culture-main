import localMapStateToProps from '../mapStateToProps'
import mockedState from './mockedState'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | mapStateToProps', () => {
  describe('When adding stock to one offer', () => {
    it('should map correctly the state', () => {
      // given
      const ownProps = {
        location: {
          search: '?lieu=DA',
        },
        match: {
          params: { offerId: 'UU' },
        },
      }

      // when
      const result = localMapStateToProps(mockedState, ownProps)
      const expected = {
        event: undefined,
        eventId: null,
        eventOccurrenceIdOrNew: undefined,
        eventOccurrencePatch: {
          beginningDatetime: '2019-03-07T13:08:37.475Z',
          endDatetime: '2019-03-07T13:08:37.475Z',
          offerId: 'UU',
          venueId: 'DA',
        },
        eventOccurrences: [],
        formBeginningDatetime: undefined,
        formBookingLimitDatetime: undefined,
        formEndDatetime: undefined,
        formPrice: undefined,
        hasIban: 'FR7630001007941234567890185',
        isEditing: false,
        isEventOccurrenceReadOnly: true,
        isStockReadOnly: true,
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-03-07T10:39:23.560392Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
          eventId: null,
          eventOccurrencesIds: [],
          id: 'UU',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          mediationsIds: ['H4'],
          modelName: 'Offer',
          stocksIds: ['MU'],
          thingId: 'LY',
          venueId: 'DA',
        },
        stockFormKey: null,
        stockIdOrNew: undefined,
        stockPatch: {
          available: 10,
          bookingLimitDatetime: null,
          bookingRecapSent: null,
          dateModified: '2019-03-07T10:40:07.318721Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
          eventOccurrenceId: null,
          groupSize: 1,
          id: 'MU',
          idAtProviders: null,
          isSoftDeleted: false,
          lastProviderId: null,
          modelName: 'Stock',
          offerId: 'UU',
          offererId: 'BA',
          price: 17,
        },
        tz: 'Europe/Paris',
        venue: {
          address: null,
          bookingEmail: 'john.doe@test.com',
          city: null,
          comment: null,
          dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
          departementCode: null,
          firstThumbDominantColor: null,
          id: 'DA',
          idAtProviders: null,
          isValidated: true,
          isVirtual: true,
          lastProviderId: null,
          latitude: 48.83638,
          longitude: 2.40027,
          managingOffererId: 'BA',
          modelName: 'Venue',
          name: 'Le Sous-sol (Offre en ligne)',
          postalCode: null,
          siret: null,
          thumbCount: 0,
          validationToken: null,
        },
        venueId: 'DA',
      }

      // then
      expect(result.offer.eventOccurrencesIds).toEqual(
        expected.offer.eventOccurrencesIds
      )
    })
  })
  describe('When eventOccurrenceIdOrNew is not present', () => {
    it('should set isEventOccurrenceReadOnly to true ', () => {
      // given
      const ownProps = {
        location: {
          search: '?lieu=DA',
        },
        match: {
          params: { offerId: 'UU' },
        },
      }

      // when
      const result = localMapStateToProps(mockedState, ownProps)

      // then
      expect(result.isEventOccurrenceReadOnly).toEqual(true)
    })
  })
})
