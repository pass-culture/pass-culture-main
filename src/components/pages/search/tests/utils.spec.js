import isInitialQueryWithoutFilters, {
  getDescriptionForSublabel,
  getFirstChangingKey,
  getRecommendationDateString,
  INITIAL_FILTER_PARAMS,
  searchResultsTitle,
  translateBrowserUrlToApiUrl,
} from '../utils'

import state from '../../../../mocks/global_state_2_Testing_10_10_18'
import { selectRecommendations } from '../../../../selectors'

const recommendations = selectRecommendations(state)

describe('src | components | pages | search | utils', () => {
  describe('getRecommendationDateString', () => {
    it('should render permanent is there is no date given', () => {
      // given
      const recommendation = recommendations[0]

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      expect(result).toEqual('permanent')
    })
    it('should render date is there is a date range for Europe/Paris Timezone', () => {
      // given
      const recommendation = recommendations[5]

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      expect(result).toEqual('du Jeudi 25/10/2018 au Vendredi 26/10/2018')
    })
    it('should render date is there is a date range for Cayenne Timezone', () => {
      // given
      const recommendation = {
        id: 'AEWP9',
        dateCreated: '2018-10-10T14:19:05.418465Z',
        dateRead: null,
        dateUpdated: '2018-10-10T14:19:05.418488Z',
        inviteforEventOccurrenceId: null,
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediation: {
          authorId: 'A83A',
          backText: null,
          credit: 'undefined',
          dateCreated: '2018-10-05T15:21:16.667011Z',
          dateModifiedAtLastProvider: '2018-10-05T15:21:16.667004Z',
          firstThumbDominantColor: [23, 24, 19],
          frontText: null,
          id: 'APQQ',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Mediation',
          offerId: 'ARCQ',
          thumbCount: 1,
          tutoIndex: null,
        },
        mediationId: 'APQQ',
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-10-05T14:33:18.717227Z',
          dateModifiedAtLastProvider: '2018-10-05T14:33:18.717221Z',
          dateRange: [
            'Thu, 25 Oct 2018 12:15:24 GMT',
            'Fri, 26 Oct 2018 1:45:24 GMT',
          ],
          eventId: 'AQCQ',
          eventOrThing: {
            accessibility: '\u0000',
            ageMax: null,
            ageMin: null,
            conditions: null,
            dateModifiedAtLastProvider: '2018-10-05T14:33:18.713422Z',
            description:
              "Proposées par l'Association Côté Court, les séances Écran Libre sont dédiées à la création contemporaine. \n\nCes rendez-vous mensuels avec  les œuvres et leurs auteurs mettent en lumière de nouvelles écritures et manières de faire du cinéma. \n\nCette fois-ci, c'est le réalisateur Christophe Loizillon qui viendra présenter trois de ses films, de format court, qui se situent entre le documentaire et la fiction. Christophe Loizillon a entre autres, participé au montage des films de Leos Carax, Christine Pascal et Alain Corneau, a été président de l'ACID pendant trois ans et intervient aujourd'hui à la Femis comme aux Beaux-Arts de Paris. Ses films lui ont valu de nombreux prix dans des festivals à l'international. \n\nLES FILMS :\n\nDETAIL, ROMAN OPALKA  - 1986, 24'  \nUn peintre obsédé par l'idée de visualiser le temps.\n\nCORPUS / CORPUS  - 2009, 26'  \nUn corps prend soin d'un autre corps. \n\nDEBOUT(S) - 2017, 28'\nDes femmes, des hommes, exerçant leur métier en position debout. ",
            durationMinutes: 90,
            extraData: null,
            firstThumbDominantColor: null,
            id: 'AQCQ',
            idAtProviders: null,
            isNational: false,
            lastProviderId: null,
            mediaUrls: [],
            modelName: 'Event',
            name: 'ÉCRAN LIBRE #2 : CHRISTOPHE LOIZILLON ',
            thumbCount: 0,
            type: 'EventType.CINEMA',
          },
          id: 'ARCQ',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Offer',
          stocks: [
            {
              available: 10,
              bookingLimitDatetime: '2018-10-23T18:15:24Z',
              bookingRecapSent: null,
              dateModified: '2018-10-05T14:35:19.200818Z',
              dateModifiedAtLastProvider: '2018-10-05T14:35:19.200812Z',
              eventOccurrence: {
                accessibility: '\u0000',
                beginningDatetime: '2018-10-25T18:15:24Z',
                dateModifiedAtLastProvider: '2018-10-05T14:34:25.281357Z',
                endDatetime: '2018-10-26T19:45:24Z',
                id: 'E7UA',
                idAtProviders: null,
                isSoftDeleted: false,
                lastProviderId: null,
                modelName: 'EventOccurrence',
                offerId: 'ARCQ',
                type: null,
              },
              eventOccurrenceId: 'E7UA',
              groupSize: 1,
              id: 'CYLQ',
              idAtProviders: null,
              isSoftDeleted: false,
              lastProviderId: null,
              modelName: 'Stock',
              offerId: null,
              price: 3,
            },
          ],
          thingId: null,
          venue: {
            address: '104 Avenue Jean Lolive',
            bookingEmail: 'contact@cotecourt.org',
            city: 'Cayenne',
            dateModifiedAtLastProvider: '2018-10-05T13:46:48.082384Z',
            departementCode: '97',
            firstThumbDominantColor: null,
            id: 'ARAQ',
            idAtProviders: null,
            isVirtual: false,
            lastProviderId: null,
            latitude: 48.89218,
            longitude: 2.40891,
            managingOfferer: {
              address: '104 AVENUE JEAN LOLIVE',
              bic: null,
              city: 'PANTIN',
              dateCreated: '2018-09-27T12:42:33.769405Z',
              dateModifiedAtLastProvider: '2018-09-27T12:42:33.769393Z',
              firstThumbDominantColor: null,
              iban: null,
              id: 'AKTQ',
              idAtProviders: null,
              isActive: true,
              lastProviderId: null,
              modelName: 'Offerer',
              name: 'ASSOCIATION COTE COURT',
              postalCode: '93500',
              siren: '400080099',
              thumbCount: 0,
            },
            managingOffererId: 'AKTQ',
            modelName: 'Venue',
            name: 'CINÉ 104',
            postalCode: '93500',
            siret: null,
            thumbCount: 0,
          },
          venueId: 'ARAQ',
        },
        offerId: 'ARCQ',
        search: null,
        shareMedium: null,
        userId: 'AQBA',
        validUntilDate: '2018-10-13T14:19:05.431082Z',
        bookingsIds: [],
      }

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      expect(result).toEqual('du Jeudi 25/10/2018 au Jeudi 25/10/2018')
    })
  })

  describe('isInitialQueryWithoutFilters', () => {
    it('should return false if there is params changed with filter', () => {
      const queryParams = {
        categories: '%C3%89couter,Pratiquer',
        date: '2018-09-25T09:38:20.576Z',
        days: null,
        distance: null,
        jours: '0-1,1-5,5-100000',
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        page: '2',
        types: null,
      }
      expect(
        isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)
      ).toEqual(false)
    })

    it('should return true if there is no params changed with filter', () => {
      const queryParams = {
        categories: null,
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
        orderBy: 'offer.id+desc',
      }
      expect(
        isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)
      ).toEqual(true)
    })
  })

  describe('getFirstChangingKey', () => {
    it('should return the name of the key wich value has changed', () => {
      const nextObject = { jours: '0-1,1-5' }
      expect(getFirstChangingKey(INITIAL_FILTER_PARAMS, nextObject)).toEqual(
        'jours'
      )
    })
  })

  describe('getDescriptionForSublabel', () => {
    it('should return the description corresponding to the label', () => {
      const typeSublabels = [
        {
          description:
            'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
          sublabel: 'Applaudir',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Jouer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Lire',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Pratiquer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Regarder',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Rencontrer',
        },
        {
          description: 'Lorem Ipsum',
          sublabel: 'Écouter',
        },
      ]
      const category = 'Applaudir'
      const result = getDescriptionForSublabel(category, typeSublabels)

      expect(result).toEqual(typeSublabels[0].description)
    })
  })

  describe('searchResultsTitle', () => {
    // given
    let items
    let keywords
    let queryParams
    let result
    let expected
    describe('with keyword search field or filter', () => {
      describe('when there is a keywords but no filters', () => {
        describe('with a search results', () => {
          it('should return number of results occurences with resultatS in plural and keyword searched', () => {
            // given
            items = [{}, {}, {}, {}]
            keywords = 'keyword'

            queryParams = {
              categories: null,
              date: null,
              days: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'keyword',
            }

            // when
            result = searchResultsTitle(keywords, items, queryParams)
            expected = '"keyword" : 4 résultats'

            // then
            expect(result).toEqual(expected)
          })
          it('should return number of results with resultat in singular and keyword searched', () => {
            // given
            items = [{}]
            keywords = 'keyword'

            queryParams = {
              categories: null,
              date: null,
              days: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'keyword',
              page: '2',
              types: null,
            }

            // when
            result = searchResultsTitle(keywords, items, queryParams)
            expected = '"keyword" : 1 résultat'

            // then
            expect(result).toEqual(expected)
          })
        })

        describe('without results', () => {
          it('should return should 0 with resultat in singular and keyword searched', () => {
            // given
            items = []
            keywords = 'keyword'
            queryParams = {
              categories: null,
              date: null,
              days: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'keyword',
              page: '2',
              types: null,
            }

            // when
            result = searchResultsTitle(keywords, items, queryParams)
            expected = '"keyword" : 0 résultat'

            // then
            expect(result).toEqual(expected)
          })
        })
      })

      describe('when there is a keyword plus one or more filters', () => {
        describe('with items in results', () => {
          it('should return a title for search results', () => {
            // given
            items = [{}, {}, {}, {}]
            keywords = 'keyword'

            queryParams = {
              categories: 'Applaudir',
              date: null,
              days: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'keyword',
            }

            // when
            result = searchResultsTitle(keywords, items, queryParams)
            expected = '"keyword" : 4 résultats'

            // then
            expect(result).toEqual(expected)
          })
        })

        describe('without items', () => {
          it('should return a title for search results', () => {
            // given
            items = []
            keywords = 'keyword'
            queryParams = {
              categories: 'Jouer',
              date: null,
              days: null,
              distance: null,
              jours: null,
              latitude: null,
              longitude: null,
              [`mots-cles`]: 'keyword',
            }

            // when
            result = searchResultsTitle(keywords, items, queryParams)
            expected = '"keyword" : 0 résultat'

            // then
            expect(result).toEqual(expected)
          })
        })
      })
    })

    describe('with navigation mode', () => {
      keywords = 'fake word'
      queryParams = {
        categories: null,
        date: null,
        days: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        [`mots-cles`]: null,
      }
      const withPagination = true

      describe('with results', () => {
        it('should not return title', () => {
          // given
          items = [{}]

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected = ''

          // then
          expect(result).toEqual(expected)
        })
      })

      describe('without no results', () => {
        it('should return a message that inform that there is no offers for the moment', () => {
          // given
          items = []

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            withPagination
          )
          expected =
            "Il n'y a pas d'offres dans cette catégorie pour le moment."

          // then
          expect(result).toEqual(expected)
        })
      })
    })
  })

  describe('src | utils | translateBrowserUrlToApiUrl ', () => {
    describe('src | utils | translateBrowserUrlToApiUrl ', () => {
      it('should return object with french key', () => {
        const queryString = {
          categories: 'Applaudir',
          date: null,
          jours: '1-5',
          [`mots-cles`]: 'fake',
        }
        const expected = {
          categories: 'Applaudir',
          date: null,
          days: '1-5',
          keywords: 'fake',
        }
        expect(translateBrowserUrlToApiUrl(queryString)).toEqual(expected)
      })
    })
  })
})
