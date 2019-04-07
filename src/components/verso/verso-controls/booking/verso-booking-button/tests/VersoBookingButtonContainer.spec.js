import { mapStateToProps } from '../VersoBookingButtonContainer'

describe('src | components | verso | verso-buttons | verso-booking-button | VersoBookingButtonContainer', () => {
  describe('mapStateToProps', () => {
    it('should map values to props', () => {
      // given
      const initialState = {
        data: {
          bookings: [{ completedUrl: 'fake url', stockId: 'C29A' }],
          recommendations: [
            {
              bookingsIds: [],
              dehumanizedId: 257,
              dehumanizedOfferId: 186,
              dehumanizedUserId: 1,
              id: 'AEAQ',
              mediationId: 'AAA',
              modelName: 'Recommendation',
              offer: {
                bookingEmail: null,
                dateCreated: '2018-09-06T08:17:50.169269Z',
                dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
                dateRange: [],
                dehumanizedEventId: null,
                dehumanizedId: 186,
                dehumanizedLastProviderId: 6,
                dehumanizedThingId: 129,
                dehumanizedVenueId: 2,
                eventId: null,
                eventOrThing: {
                  dateModifiedAtLastProvider: '2018-01-30T00:00:00Z',
                  dehumanizedId: 129,
                  dehumanizedLastProviderId: 8,
                  description: null,
                  extraData: {
                    author: 'Jouve, Jessica ;Dufour, Anthony',
                    dewey: '840',
                    num_in_collection: '0',
                    prix_livre: '12.90',
                    rayon: 'Littérature française',
                    titelive_regroup: '0',
                  },
                  firstThumbDominantColor: [12, 62, 123],
                  id: 'QE',
                  idAtProviders: '9782367740911',
                  isActive: false,
                  lastProviderId: 'BA',
                  mediaUrls: [],
                  modelName: 'Thing',
                  name: 'sur la route des migrants ; rencontres à Calais',
                  thumbCount: 2,
                  type: 'Book',
                  url: null,
                },
                id: 'ASKA',
                idAtProviders: '2921:9782367740911',
                isFinished: false,
                lastProviderId: 'AY',
                modelName: 'Offer',
                stocks: [
                  {
                    available: 10,
                    beginningDatetime: '2018-12-30T18:30:39Z',
                    bookingLimitDatetime: '2018-12-28T18:30:39Z',
                    bookingRecapSent: null,
                    dateModified: '2018-10-11T09:34:21.382659Z',
                    dateModifiedAtLastProvider: '2018-10-11T09:34:21.382638Z',
                    endDatetime: '2018-12-31T22:30:39Z',
                    groupSize: 1,
                    id: 'C29A',
                    idAtProviders: null,
                    isSoftDeleted: false,
                    lastProviderId: null,
                    modelName: 'Stock',
                    offerId: 'ASKA',
                    price: 15,
                  },
                ],
                thingId: 'QE',
                venue: {
                  address: '72 rue Carnot',
                  bookingEmail: 'passculture-dev@beta.gouv.fr',
                  city: 'ROMAINVILLE',
                  dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
                  dehumanizedId: 2,
                  dehumanizedLastProviderId: 7,
                  dehumanizedManagingOffererId: 2,
                  departementCode: '93',
                  firstThumbDominantColor: null,
                  id: 'A9',
                  idAtProviders: '2921',
                  isVirtual: false,
                  lastProviderId: 'A4',
                  latitude: 2.44072,
                  longitude: 48.88381,
                  managingOfferer: {
                    address: '72 rue Carnot',
                    city: 'ROMAINVILLE',
                    dateCreated: '2018-09-06T08:16:23.133432Z',
                    dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
                    dehumanizedId: 2,
                    dehumanizedLastProviderId: 7,
                    firstThumbDominantColor: null,
                    id: 'A9',
                    idAtProviders: '2921',
                    isActive: true,
                    lastProviderId: 'A4',
                    modelName: 'Offerer',
                    name: 'Les Pipelettes',
                    postalCode: '93230',
                    siren: '302559639',
                    thumbCount: 0,
                  },
                  managingOffererId: 'A9',
                  modelName: 'Venue',
                  name: 'Les Pipelettes',
                  postalCode: '93230',
                  siret: '30255963934017',
                  thumbCount: 0,
                },
                venueId: 'A9',
              },
              offerId: 'ASKA',
              search: 'route',
              shareMedium: null,
              userId: 'AE',
              validUntilDate: '2018-09-11T14:27:31.798174Z',
            },
          ],
        },
        geolocation: {
          latitude: 41,
          longitude: 42,
        },
      }
      const router = {
        location: {
          search: 'fake search',
        },
        match: {
          params: {
            mediationId: 'AAA',
            offerId: 'ASKA',
          },
        },
      }
      const expectResult = {
        booking: {
          completedUrl: 'fake url',
          stockId: 'C29A',
        },
        isFinished: false,
        locationSearch: 'fake search',
        onlineOfferUrl: 'fake url',
      }

      // when
      const result = mapStateToProps(initialState, router)

      // then
      expect(result).toEqual(expectResult)
    })
  })
})
