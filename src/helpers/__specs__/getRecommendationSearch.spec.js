import { DEFAULT_MAX_DISTANCE } from '../../components/pages/search/helpers'
import { getRecommendationSearch } from '../getRecommendationSearch'
import state from '../../mocks/state'

const types = state.data.types

describe('src | helpers | getRecommendationSearch', () => {
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

    it('should return nothing when type is null', () => {
      // given
      const search = 'categories=Applaudir,Jouer'

      // when
      const recommendationSearch = getRecommendationSearch(search, null)

      // then
      expect(recommendationSearch).toBe('')
    })
  })
})
