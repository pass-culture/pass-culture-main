import selectRecommendationsBySearchQuery, {
  getRecommendationSearch,
} from '../selectRecommendationsBySearchQuery'
import state from '../../../../../mocks/stateWithTypes'

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

    it('should return categories', () => {
      // given
      const search = 'categories=Applaudir,Jouer'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe(
        "type_values=['EventType.JEUX', 'EventType.SPECTACLE_VIVANT', 'ThingType.JEUX_ABO', 'ThingType.JEUX_VIDEO']"
      )
    })

    it('should return date', () => {
      // given
      const search = 'date=2019-09-05T15%3A12%3A57.008Z&jours=1-5%2C5-100000&page=1'

      // when
      const recommendationSearch = getRecommendationSearch(search, types)

      // then
      expect(recommendationSearch).toBe(
        'days_intervals=[[datetime.datetime(2019, 9, 6, 15, 12, 57, 008000, tzinfo=tzlocal()), datetime.datetime(2019, 9, 10, 15, 12, 57, 008000, tzinfo=tzlocal())], [datetime.datetime(2019, 9, 10, 15, 12, 57, 008000, tzinfo=tzlocal()), datetime.datetime(2293, 6, 20, 15, 12, 57, 008000, tzinfo=tzlocal())]]'
      )
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
          search: 'keywords_string=mimi',
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
  })
})
