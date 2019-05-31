import localMapStateToProps from '../mapStateToProps'
import state from '../../../../../utils/mocks/state'

describe('src | components | pages | Offer | StockItem | mapStateToProps', () => {
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
        query: {
          parse: () => ({}),
        },
      }

      // when
      const result = localMapStateToProps(state, ownProps)
      const expected = {
        event: undefined,
        formBeginningDatetime: undefined,
        formBookingLimitDatetime: undefined,
        formEndDatetime: undefined,
        formPrice: undefined,
        hasIban: 'FR7630001007941234567890185',
        isStockReadOnly: true,
        offer: {
          bookingEmail: 'booking.email@test.com',
          dateCreated: '2019-03-07T10:39:23.560392Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
          isEvent: false,
          isThing: true,
          id: 'UU',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          mediationsIds: ['H4'],
          modelName: 'Offer',
          productId: 'LY',
          stocksIds: ['MU'],
          venueId: 'DA',
        },
        stockFormKey: null,
        stockIdOrNew: undefined,
        formInitialValues: {
          available: 10,
          bookingLimitDatetime: null,
          bookingRecapSent: null,
          dateModified: '2019-03-07T10:40:07.318721Z',
          dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
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
      expect(result.offer).toEqual(expected.offer)
    })
  })
})
