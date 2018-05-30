import { createSelector } from 'reselect'

import getDistance from '../getters/distance'


const emptyRecommendations = []

export default createSelector(
  state => state.data.recommendations || emptyRecommendations,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (recommendations, latitude, longitude) => {
    if (!latitude || !longitude) {
      return recommendations
    }
    const sortedRecommendations = recommendations.map(recommendation => {
      recommendation.distance = getDistance(recommendation, latitude, longitude)
      return recommendation
    }).filter(recommendation => recommendation.distance)
    // closest one at the beginning
    sortedRecommendations.sort((recommendation1, recommendation2) =>
      recommendation1.distance - recommendation2.distance)
    return sortedRecommendations
  }
)
