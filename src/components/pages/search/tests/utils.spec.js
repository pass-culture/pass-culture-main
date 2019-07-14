import {
  getDescriptionFromCategory,
  getFirstChangingKey,
  getRecommendationDateString,
  INITIAL_FILTER_PARAMS,
  isInitialQueryWithoutFilters,
  searchResultsTitle,
  translateBrowserUrlToApiUrl,
  isDaysChecked,
} from '../utils'

describe('src | components | pages | search | utils', () => {
  describe('getRecommendationDateString', () => {
    it('should render permanent if there is no date given', () => {
      // given
      const recommendation = {
        offer: {
          dateRange: [],
        },
      }

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      expect(result).toBe('permanent')
    })

    it('should render date if there is a date range for Europe/Paris Timezone', () => {
      // given
      const recommendation = {
        offer: {
          dateRange: ['Thu, 25 Oct 2018 18:15:24 GMT', 'Fri, 26 Oct 2018 19:45:24 GMT'],
          venue: {
            departementCode: '93',
          },
        },
      }

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      // https://github.com/nodejs/node-v0.x-archive/issues/4689
      expect(result).toBe('du Thu 2018-10-25 au Fri 2018-10-26')
    })

    it('should render date if there is a date range for Cayenne Timezone', () => {
      // given
      const recommendation = {
        offer: {
          dateRange: ['Thu, 25 Oct 2018 12:15:24 GMT', 'Fri, 26 Oct 2018 1:45:24 GMT'],
          venue: {
            departementCode: '97',
          },
        },
        offerId: 'ARCQ',
      }

      // when
      const result = getRecommendationDateString(recommendation.offer)

      // then
      // https://github.com/nodejs/node-v0.x-archive/issues/4689
      expect(result).toBe('du Thu 2018-10-25 au Thu 2018-10-26')
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
      expect(isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)).toBe(false)
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
      expect(isInitialQueryWithoutFilters(INITIAL_FILTER_PARAMS, queryParams)).toBe(true)
    })
  })

  describe('getFirstChangingKey', () => {
    it('should return the name of the key wich value has changed', () => {
      const nextObject = { jours: '0-1,1-5' }
      expect(getFirstChangingKey(INITIAL_FILTER_PARAMS, nextObject)).toBe('jours')
    })
  })

  describe('getDescriptionFromCategory', () => {
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
      const result = getDescriptionFromCategory(category, typeSublabels)

      expect(result).toBe(typeSublabels[0].description)
    })
  })

  describe('searchResultsTitle', () => {
    // given
    let items
    let keywords
    let queryParams
    let result
    let expected
    let cameFromOfferTypesPage
    let hasReceivedFirstSuccessData
    describe('with keyword search field or filter', () => {
      describe('when there is a keywords but no filters', () => {
        describe('with a search results', () => {
          it('should return number of results occurences with resultatS in plural and keyword searched', () => {
            // given
            cameFromOfferTypesPage = false
            hasReceivedFirstSuccessData = true
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
            result = searchResultsTitle(
              keywords,
              items,
              cameFromOfferTypesPage,
              hasReceivedFirstSuccessData
            )

            // then
            expected = '"keyword" : 4 résultats'
            expect(result).toBe(expected)
          })

          it('should return number of results with resultat in singular and keyword searched', () => {
            // given
            cameFromOfferTypesPage = false
            hasReceivedFirstSuccessData = true
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
            result = searchResultsTitle(
              keywords,
              items,
              cameFromOfferTypesPage,
              hasReceivedFirstSuccessData
            )

            // then
            expected = '"keyword" : 1 résultat'
            expect(result).toBe(expected)
          })
        })

        describe('without results', () => {
          it('should return should 0 with resultat in singular and keyword searched', () => {
            // given
            cameFromOfferTypesPage = false
            hasReceivedFirstSuccessData = true
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
            result = searchResultsTitle(
              keywords,
              items,
              cameFromOfferTypesPage,
              hasReceivedFirstSuccessData
            )

            // then
            expected = '"keyword" : 0 résultat'
            expect(result).toBe(expected)
          })
        })
      })

      describe('when there is a keyword plus one or more filters', () => {
        describe('with items in results', () => {
          it('should return a title for search results', () => {
            // given
            cameFromOfferTypesPage = false
            hasReceivedFirstSuccessData = true
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
            result = searchResultsTitle(
              keywords,
              items,
              cameFromOfferTypesPage,
              hasReceivedFirstSuccessData
            )

            // then
            expected = '"keyword" : 4 résultats'
            expect(result).toBe(expected)
          })
        })

        describe('without items', () => {
          it('should return a title for search results', () => {
            // given
            cameFromOfferTypesPage = false
            hasReceivedFirstSuccessData = true
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
            result = searchResultsTitle(
              keywords,
              items,
              cameFromOfferTypesPage,
              hasReceivedFirstSuccessData
            )

            // then
            expected = '"keyword" : 0 résultat'
            expect(result).toBe(expected)
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

      describe('with results', () => {
        it('should not return title', () => {
          // given
          cameFromOfferTypesPage = true
          hasReceivedFirstSuccessData = true
          items = [{}]

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            cameFromOfferTypesPage,
            hasReceivedFirstSuccessData
          )

          // then
          expected = ''
          expect(result).toBe(expected)
        })
      })

      describe('without no results', () => {
        it('should return a message that inform that there is no offers for the moment', () => {
          // given
          cameFromOfferTypesPage = true
          hasReceivedFirstSuccessData = true
          items = []

          // when
          result = searchResultsTitle(
            keywords,
            items,
            queryParams,
            cameFromOfferTypesPage,
            hasReceivedFirstSuccessData
          )

          // then
          expected = 'Il n’y a pas d’offres dans cette catégorie pour le moment.'
          expect(result).toBe(expected)
        })
      })
    })
  })

  describe('translateBrowserUrlToApiUrl ', () => {
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
        expect(translateBrowserUrlToApiUrl(queryString)).toStrictEqual(expected)
      })
    })
  })

  describe('isDaysChecked()', () => {
    describe('date is picked in calendar', () => {
      it('should not check date', () => {
        // given
        const pickedDate = new Date('2019-06-02T12:41:33.680Z')

        // when
        const result = isDaysChecked(pickedDate)

        // then
        expect(result).toBe(false)
      })
    })

    describe('date is picked with a checkbox', () => {
      it('should check box when chosen date is in date range', () => {
        // given
        const pickedDate = null
        const pickedDaysInQuery = '0-1,5-10000'
        const inputValue = '0-1'

        // when
        const result = isDaysChecked(pickedDate, pickedDaysInQuery, inputValue)

        // then
        expect(result).toBe(true)
      })

      it('should not check when chosen date is not in date range', () => {
        // given
        const pickedDate = null
        const pickedDaysInQuery = '1-5'
        const inputValue = '0-1'

        // when
        const result = isDaysChecked(pickedDate, pickedDaysInQuery, inputValue)

        // then
        expect(result).toBe(false)
      })
    })
  })
})
