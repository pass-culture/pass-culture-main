import createCachedSelector from 're-reselect'
import { createSelector } from 'reselect'

import { getRecommendationSearch } from '../../helpers/getRecommendationSearch'
import removePageFromSearchString from '../../helpers/removePageFromSearchString'
import { selectBookingByRouterMatch } from './bookingsSelectors'
import { selectFavoriteById } from './favoritesSelectors'

export const selectRecommendations = state => state.data.recommendations

export const selectRecommendationById = createCachedSelector(
  state => state.data.recommendations,
  (state, recommendationId) => recommendationId,
  (recommendations, recommendationId) =>
    recommendations.find(recommendation => recommendation.id === recommendationId)
)((state, recommendationId = '') => recommendationId)

export const selectRecommendationsBySearchQuery = createSelector(
  state => state.data.recommendations,
  state => state.data.types,
  (state, location) => removePageFromSearchString(location.search),
  (recommendations, types, searchWithoutPage) => {
    const searchQuery = getRecommendationSearch(searchWithoutPage, types)
    return recommendations.filter(recommendation => {
      if (recommendation.search === null) {
        return false
      }

      const searchRecommendationWithoutPage = removePageFromSearchString(recommendation.search)
      return searchRecommendationWithoutPage === decodeURIComponent(searchQuery)
    })
  }
)

export const selectRecommendationByOfferIdAndMediationId = createCachedSelector(
  state => state.data.recommendations,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (recommendations, offerId, mediationId) =>
    recommendations.find(recommendation => {
      const matchOffer = recommendation.offerId === offerId
      const matchMediation = recommendation.mediationId === mediationId
      return matchMediation || matchOffer
    })
)((state, offerId = '', mediationId = '') => `${offerId}${mediationId}`)

export const selectRecommendationByRouterMatch = createCachedSelector(
  state => state.data.recommendations,
  (state, match) =>
    selectRecommendationByOfferIdAndMediationId(
      state,
      match.params.offerId,
      match.params.mediationId
    ),
  selectBookingByRouterMatch,
  (state, match) => selectFavoriteById(state, match.params.favoriteId),
  (recommendations, recommendation, booking, favorite) => {
    if (recommendation) {
      return recommendation
    }
    if (booking) {
      return selectRecommendationById({ data: { recommendations } }, booking.recommendationId)
    }
    if (favorite) {
      return selectRecommendationByOfferIdAndMediationId(
        { data: { recommendations } },
        favorite.offerId,
        favorite.mediationId
      )
    }
  }
)((state, match) => {
  const { params } = match
  const { bookingId, favoriteId, mediationId, offerId } = params
  return `${bookingId || ' '}${favoriteId || ' '}${mediationId || ' '}${offerId || ' '}`
})
