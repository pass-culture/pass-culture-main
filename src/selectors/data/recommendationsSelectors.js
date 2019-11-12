import { createSelector } from 'reselect'
import { getRecommendationSearch } from '../../helpers/getRecommendationSearch'
import removePageFromSearchString from '../../helpers/removePageFromSearchString'

export const selectRecommendations = state => state.data.recommendations

export const selectRecommendationsBySearchQuery = createSelector(
  state => state.data.recommendations,
  state => state.data.types,
  (state, location) => removePageFromSearchString(location.search),
  (recommendations, types, searchWithoutPage) => {
    const searchQuery = getRecommendationSearch(searchWithoutPage, types)
    let filteredRecommendations = recommendations.filter(recommendation => {
      if (recommendation.search === null) {
        return false
      }

      const searchRecommendationWithoutPage = removePageFromSearchString(recommendation.search)
      return searchRecommendationWithoutPage === decodeURIComponent(searchQuery)
    })
    return filteredRecommendations
  }
)
