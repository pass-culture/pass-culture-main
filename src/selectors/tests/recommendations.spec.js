import { selectRecommendations } from '../recommendations'
import state2 from '../../mocks/global_state_2_Testing_10_10_18'

describe('selectRecommendations', () => {
  it('should return an array of object having an `uniqId` property', () => {
    // Given
    const state = state2
    // When
    const results = selectRecommendations(state)
    // Then
    expect(results).not.toHaveLength(0)
    results.forEach(result => {
      expect(result.uniqId).toBeDefined()
    })
  })

  it('should return an empty array if there are no recommendations', () => {
    // given
    const state = {
      data: {
        recommendations: [],
      },
      geolocation: {
        latitude: 48.8637,
        longitude: 2.3374,
        watchId: 1,
      },
    }

    // when
    const result = selectRecommendations(state)

    // then
    expect(result).toEqual([])
  })

  it('should return recommendations', () => {
    // given
    const expected = {
      bookingsIds: [],
      dateCreated: '2018-10-10T14:19:27.410551Z',
      dateRead: null,
      dateUpdated: '2018-10-10T14:19:27.410609Z',
      distance: '5444 km',
      firstThumbDominantColor: [237, 235, 231],
      id: 'AEWPS',
      index: 0,
      isClicked: true,
      isFavorite: false,
      isFirst: false,
      mediation: {
        authorId: 'AMTQ',
        backText: null,
        credit: 'undefined',
        dateCreated: '2018-09-12T08:35:27.948370Z',
        dateModifiedAtLastProvider: '2018-09-12T08:35:27.948349Z',
        firstThumbDominantColor: [237, 235, 231],
        frontText: null,
        id: 'AKSA',
        idAtProviders: null,
        isActive: true,
        lastProviderId: null,
        modelName: 'Mediation',
        offerId: 'AKLA',
        thumbCount: 1,
        tutoIndex: null,
      },
      mediationId: 'AKSA',
      modelName: 'Recommendation',
      offer: {
        bookingEmail: null,
        dateCreated: '2018-09-12T08:19:01.614549Z',
        dateModifiedAtLastProvider: '2018-09-12T08:19:01.614532Z',
        dateRange: [],
        eventId: null,
        eventOrThing: {
          dateModifiedAtLastProvider: '2018-09-12T08:19:01.612018Z',
          description:
            'LA TOILE est une plateforme VOD qui vous propose une programmation complémentaire en lien avec VOTRE salle de cinéma. ',
          extraData: null,
          firstThumbDominantColor: null,
          id: 'BE',
          idAtProviders: null,
          isNational: false,
          lastProviderId: null,
          mediaUrls: [],
          modelName: 'Thing',
          name: 'La Toile VOD',
          thumbCount: 0,
          type: 'AUDIOVISUEL',
          url: 'https://www.la-toile-vod.com/login',
        },
        id: 'AKLA',
        idAtProviders: null,
        isActive: true,
        lastProviderId: null,
        modelName: 'Offer',
        stocks: [
          {
            available: 200,
            beginningDatetime: null,
            bookingLimitDatetime: null,
            bookingRecapSent: null,
            dateModified: '2018-09-12T15:13:50.187143Z',
            dateModifiedAtLastProvider: '2018-09-12T15:13:50.187134Z',
            endDatetime: null,
            groupSize: 1,
            id: 'C8PA',
            idAtProviders: null,
            isSoftDeleted: false,
            lastProviderId: null,
            modelName: 'Stock',
            offerId: 'AKLA',
            price: 3,
          },
        ],
        thingId: 'BE',
        venue: {
          address: null,
          bookingEmail: null,
          city: null,
          dateModifiedAtLastProvider: '2018-09-12T08:15:18.450460Z',
          departementCode: null,
          firstThumbDominantColor: null,
          id: 'AMLA',
          idAtProviders: null,
          isVirtual: true,
          lastProviderId: null,
          latitude: null,
          longitude: null,
          managingOfferer: {
            address: '15 RUE FENELON',
            bic: null,
            city: 'PARIS 10',
            dateCreated: '2018-09-12T08:15:18.438270Z',
            dateModifiedAtLastProvider: '2018-09-12T08:15:18.438257Z',
            firstThumbDominantColor: null,
            iban: null,
            id: 'A9EA',
            idAtProviders: null,
            isActive: true,
            lastProviderId: null,
            modelName: 'Offerer',
            name: 'CARBEC MEDIA',
            postalCode: '75010',
            siren: '818194870',
            thumbCount: 0,
          },
          managingOffererId: 'A9EA',
          modelName: 'Venue',
          name: 'Offre en ligne',
          postalCode: null,
          siret: null,
          thumbCount: 0,
        },
        venueId: 'AMLA',
      },
      offerId: 'AKLA',
      search: 'page=1',
      shareMedium: null,
      thumbUrl: 'http://localhost/storage/thumbs/mediations/AKSA',
      tz: 'Europe/Paris',
      uniqId: 'thing_BE',
      userId: 'AQBA',
      validUntilDate: '2018-10-13T14:19:27.442986Z',
    }

    // when
    const result = selectRecommendations(state2)

    // then
    expect(result[0]).toEqual(expected)
    expect(result.length).toEqual(46)
  })

  describe('computes rounded distances', () => {
    describe('when recommendation and user are less than 30 meters away', () => {
      it('should return 6 meters', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.8638,
                    longitude: 2.3375,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: 48.863749399999996,
            longitude: 2.3374608,
            watchId: 1,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('6 m')
      })
    })
    describe('when recommendation and user are less than 100 meters away', () => {
      it('should return 65 meters when distance is 66.79 meters', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.8643,
                    longitude: 2.3374,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 1,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('65 m')
      })
    })
    describe('when recommendation and user are less than 1000 meters away', () => {
      it('should return 470 meters when distance is 473.10 meters', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.86795,
                    longitude: 2.3374,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 1,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('470 m')
      })
    })
    describe('when recommendation and user are less than 5000 meters away', () => {
      it('should return 2.2 kilometers when distance is 2226.38 meters', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.8437,
                    longitude: 2.3374,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 1,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('2.2 km')
      })
    })
    describe('when recommendation and user are more than 5000 meters away', () => {
      it('should return 17 kilometers when distance is 16697.92 meters', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.7137,
                    longitude: 2.3374,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 1,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('17 km')
      })
    })
  })

  describe('does not compute rounded distances', () => {
    describe('when there is no geolocation for the user', () => {
      it('returns "-" as distance', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                id: 'AEWPS',
                offer: {
                  thingId: 'BE',
                  venue: {
                    latitude: 48.7137,
                    longitude: 2.3374,
                  },
                  venueId: 'AMLA',
                },
                offerId: 'AKLA',
              },
            ],
          },
          geolocation: {
            latitude: null,
            longitude: null,
            watchId: 0,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('-')
      })
    })
    describe('when there is no offer for the recommendation', () => {
      it('returns "-" as distance', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                bookingsIds: [],
                dateCreated: '2018-10-10T14:19:27.410551Z',
                dateRead: null,
                dateUpdated: '2018-10-10T14:19:27.410609Z',
                id: 'AEWPS',
                inviteforEventOccurrenceId: null,
                isClicked: true,
                isFavorite: false,
                isFirst: false,
                mediation: {
                  authorId: 'AMTQ',
                  backText: null,
                  credit: 'undefined',
                  dateCreated: '2018-09-12T08:35:27.948370Z',
                  dateModifiedAtLastProvider: '2018-09-12T08:35:27.948349Z',
                  firstThumbDominantColor: [237, 235, 231],
                  frontText: null,
                  id: 'AKSA',
                  idAtProviders: null,
                  isActive: true,
                  lastProviderId: null,
                  modelName: 'Mediation',
                  offerId: 'AKLA',
                  thumbCount: 1,
                  tutoIndex: null,
                },
                mediationId: 'AKSA',
                modelName: 'Recommendation',
                search: 'page=1',
                shareMedium: null,
                userId: 'AQBA',
                validUntilDate: '2018-10-13T14:19:27.442986Z',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 0,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('-')
      })
    })
    describe('when there is no venue for the recommendation', () => {
      it('returns "-" as distance', () => {
        // given
        const state = {
          data: {
            recommendations: [
              {
                bookingsIds: [],
                dateCreated: '2018-10-10T14:19:27.410551Z',
                dateRead: null,
                dateUpdated: '2018-10-10T14:19:27.410609Z',
                id: 'AEWPS',
                inviteforEventOccurrenceId: null,
                isClicked: true,
                isFavorite: false,
                isFirst: false,
                mediation: {
                  authorId: 'AMTQ',
                  backText: null,
                  credit: 'undefined',
                  dateCreated: '2018-09-12T08:35:27.948370Z',
                  dateModifiedAtLastProvider: '2018-09-12T08:35:27.948349Z',
                  firstThumbDominantColor: [237, 235, 231],
                  frontText: null,
                  id: 'AKSA',
                  idAtProviders: null,
                  isActive: true,
                  lastProviderId: null,
                  modelName: 'Mediation',
                  offerId: 'AKLA',
                  thumbCount: 1,
                  tutoIndex: null,
                },
                mediationId: 'AKSA',
                modelName: 'Recommendation',
                offer: {
                  bookingEmail: null,
                  dateCreated: '2018-09-12T08:19:01.614549Z',
                  dateModifiedAtLastProvider: '2018-09-12T08:19:01.614532Z',
                  dateRange: [],
                  eventId: null,
                  eventOrThing: {
                    dateModifiedAtLastProvider: '2018-09-12T08:19:01.612018Z',
                    description:
                      'LA TOILE est une plateforme VOD qui vous propose une programmation complémentaire en lien avec VOTRE salle de cinéma. ',
                    extraData: null,
                    firstThumbDominantColor: null,
                    id: 'BE',
                    idAtProviders: null,
                    isNational: false,
                    lastProviderId: null,
                    mediaUrls: [],
                    modelName: 'Thing',
                    name: 'La Toile VOD',
                    thumbCount: 0,
                    type: 'AUDIOVISUEL',
                    url: 'https://www.la-toile-vod.com/login',
                  },
                  id: 'AKLA',
                  idAtProviders: null,
                  isActive: true,
                  lastProviderId: null,
                  modelName: 'Offer',
                  stocks: [
                    {
                      available: 200,
                      beginningDatetime: null,
                      bookingLimitDatetime: null,
                      bookingRecapSent: null,
                      dateModified: '2018-09-12T15:13:50.187143Z',
                      dateModifiedAtLastProvider: '2018-09-12T15:13:50.187134Z',
                      endDatetime: null,
                      groupSize: 1,
                      id: 'C8PA',
                      idAtProviders: null,
                      isSoftDeleted: false,
                      lastProviderId: null,
                      modelName: 'Stock',
                      offerId: 'AKLA',
                      price: 3,
                    },
                  ],
                  thingId: 'BE',
                },
                offerId: 'AKLA',
                search: 'page=1',
                shareMedium: null,
                userId: 'AQBA',
                validUntilDate: '2018-10-13T14:19:27.442986Z',
              },
            ],
          },
          geolocation: {
            latitude: 48.8637,
            longitude: 2.3374,
            watchId: 0,
          },
        }

        // when
        const result = selectRecommendations(state)

        // then
        expect(result[0].distance).toEqual('-')
      })
    })
  })
})
