import { DEFAULT_MAX_DISTANCE } from '../../helpers'
import selectRecommendationsBySearchQuery, {
  getRecommendationSearch,
  removePageFromSearchString,
} from '../selectRecommendationsBySearchQuery'
import state from '../../../../../mocks/state'

const types = state.data.types

describe('src | components | pages | search | selectors | selectRecommendationsBySearchQuery', () => {
  describe('getRecommendationSearch', () => {
    it('should return keywords_string', () => {
      // given
      const search = 'mots-cles=mimi'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe('keywords_string=mimi')
    })

    it('should return max_distance', () => {
      // given
      const search = 'distance=500&latitude=1.3&longitude=0.45'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe('latitude=1.3&longitude=0.45&max_distance=500.0')
    })

    it('should not return max_distance if distance is set to max : "20000"', () => {
      // given
      const search = `'distance=${DEFAULT_MAX_DISTANCE}&latitude=1.3&longitude=0.45'`

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe('')
    })

    it('should return categories', () => {
      // given
      const search = 'categories=Applaudir,Jouer'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe(
        "type_values=['EventType.JEUX', 'EventType.SPECTACLE_VIVANT', 'ThingType.SPECTACLE_VIVANT_ABO', 'ThingType.JEUX_ABO', 'ThingType.JEUX_VIDEO']"
      )
    })

    it('should return categories Écouter', () => {
      // given
      const search = 'categories=%25C3%2589couter'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe(
        "type_values=['EventType.MUSIQUE', 'ThingType.MUSIQUE_ABO', 'ThingType.MUSIQUE']"
      )
    })

    it('should return date', () => {
      // given
      const search = 'date=2019-09-05T15%3A12%3A57.008Z&jours=1-5%2C5-100000'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe(
        'days_intervals=[[datetime.datetime(2019, 9, 6, 15, 12, 57, 008000, tzinfo=tzlocal()), datetime.datetime(2019, 9, 10, 15, 12, 57, 008000, tzinfo=tzlocal())], [datetime.datetime(2019, 9, 10, 15, 12, 57, 008000, tzinfo=tzlocal()), datetime.datetime(2293, 6, 20, 15, 12, 57, 008000, tzinfo=tzlocal())]]'
      )
    })

    it('should return number of page', () => {
      // given
      const search = 'mots-cles=yo&page=666'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe('keywords_string=yo&page=666')
    })
  })

  describe('selectRecommendationsBySearchQuery', () => {
    it('should select only recommendations from a specific search', () => {
      // given
      const currentSearchRecommendations = [
        {
          id: 'AE',
          productOrTutoIdentifier: 'product_GU',
          search: 'keywords_string=mimi',
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GV',
          search: 'keywords_string=mimi&page=13',
        },
      ]
      const oldSearchRecommendations = [
        {
          id: 'CG',
          productOrTutoIdentifier: 'product_GL',
          search: 'keywords_string=toto',
        },
        {
          id: 'DH',
          productOrTutoIdentifier: 'product_GM',
          search: 'keywords_string=toto',
        },
      ]
      const fromDiscoveryRecommendations = [
        {
          id: 'HK',
          productOrTutoIdentifier: 'product_GZ',
          search: null,
        },
      ]
      const state = {
        data: {
          recommendations: [
            ...currentSearchRecommendations,
            ...fromDiscoveryRecommendations,
            ...oldSearchRecommendations,
          ],
          types,
        },
      }
      const location = {
        search: 'mots-cles=mimi',
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual(currentSearchRecommendations)
    })

    it('should select recommendations from a search combining keywords and category', () => {
      // given
      const currentSearchedRecommendations = [
        {
          id: 'AE',
          productOrTutoIdentifier: 'product_GU',
          search:
            "keywords_string=narval&page=1&type_values=['EventType.MUSIQUE', 'ThingType.MUSIQUE_ABO', 'ThingType.MUSIQUE']",
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GV',
          search:
            "keywords_string=narval&page=12&type_values=['EventType.MUSIQUE', 'ThingType.MUSIQUE_ABO', 'ThingType.MUSIQUE']",
        },
      ]
      const state = {
        data: {
          recommendations: [...currentSearchedRecommendations],
          types,
        },
      }
      const location = {
        search: 'mots-cles=narval&page=12&categories=Écouter',
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual(currentSearchedRecommendations)
    })

    it('should select recommendations from a category search', () => {
      // given
      const currentSearchedRecommendations = [
        {
          id: 'AE',
          productOrTutoIdentifier: 'product_GU',
          search:
            "page=2&type_values=['ThingType.LIVRE_EDITION', 'ThingType.LIVRE_AUDIO', 'ThingType.PRESSE_ABO']",
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GV',
          search:
            "page=251&type_values=['ThingType.LIVRE_EDITION', 'ThingType.LIVRE_AUDIO', 'ThingType.PRESSE_ABO']",
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GT',
          search:
            "type_values=['ThingType.LIVRE_EDITION', 'ThingType.LIVRE_AUDIO', 'ThingType.PRESSE_ABO']",
        },
      ]

      const state = {
        data: {
          recommendations: [...currentSearchedRecommendations],
          types,
        },
      }

      const location = {
        search: '?categories=Lire',
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual(currentSearchedRecommendations)
    })

    it('should select recommendations from a distance less than 10 km search', () => {
      // given
      const currentSearchedRecommendations = [
        {
          id: 'AE',
          productOrTutoIdentifier: 'product_GU',
          search:
            "latitude=48.86&longitude=2.34&max_distance=50.0&page=1&type_values=['EventType.SPECTACLE_VIVANT', 'ThingType.SPECTACLE_VIVANT_ABO']",
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GV',
          search:
            "latitude=48.86&longitude=2.34&max_distance=50.0&type_values=['EventType.SPECTACLE_VIVANT', 'ThingType.SPECTACLE_VIVANT_ABO']",
        },
      ]

      const state = {
        data: {
          recommendations: [...currentSearchedRecommendations],
          types,
        },
      }

      const location = {
        search: '?categories=Applaudir&distance=50&latitude=48.86&longitude=2.34',
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual(currentSearchedRecommendations)
    })

    it('should select recommendations with "Toutes distances" search', () => {
      // given
      const currentSearchedRecommendations = [
        {
          id: 'AE',
          productOrTutoIdentifier: 'product_GU',
          search:
            "page=1&type_values=['EventType.SPECTACLE_VIVANT', 'ThingType.SPECTACLE_VIVANT_ABO']",
        },
        {
          id: 'BF',
          productOrTutoIdentifier: 'product_GV',
          search: "type_values=['EventType.SPECTACLE_VIVANT', 'ThingType.SPECTACLE_VIVANT_ABO']",
        },
      ]

      const state = {
        data: {
          recommendations: [...currentSearchedRecommendations],
          types,
        },
      }

      const location = {
        search: `?categories=Applaudir&distance=${DEFAULT_MAX_DISTANCE}&latitude=48.86320299867651&longitude=2.343763285384099`,
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual(currentSearchedRecommendations)
    })

    it('should retrieve recommendation with "?" in search', () => {
      // given
      const state = {
        data: {
          recommendations: [
            {
              id: 'AE',
              search: 'keywords_string=MENSCH ! SONT LES HOMMES ?&page=1',
            },
          ],
        },
      }

      const location = {
        search: 'mots-cles=MENSCH ! SONT LES HOMMES %3F&page=1',
      }

      // when
      const recommendations = selectRecommendationsBySearchQuery(state, location)

      // then
      expect(recommendations).toStrictEqual([
        {
          id: 'AE',
          search: 'keywords_string=MENSCH ! SONT LES HOMMES ?&page=1',
        },
      ])
    })
  })

  describe('removePageFromSearchString', () => {
    it('should remove page when page is at beginning of the string', () => {
      // given
      const searchString = "page=251&type_values=['ThingType.LIVRE_EDITION']"

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe("type_values=['ThingType.LIVRE_EDITION']")
    })

    it('should remove page when page is inside the string', () => {
      // given
      const searchString = "keywords_string=narval&page=12&type_values=['EventType.MUSIQUE']"

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe("keywords_string=narval&type_values=['EventType.MUSIQUE']")
    })

    it('should remove page when page is at end of the string ', () => {
      // given
      const searchString = 'keywords_string=mimi&page=130112'

      // when
      const result = removePageFromSearchString(searchString)

      // then
      expect(result).toBe('keywords_string=mimi')
    })
  })
})
