import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { computeDistanceInMeters, humanizeDistance } from '../utils/geolocation'
import { getTimezone } from '../utils/timezone'
import { setUniqIdOnRecommendation } from '../utils/recommendation'

export const selectRecommendations = createSelector(
  state => state.data.recommendations,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (recommendations, latitude, longitude) => {
    // RECOMMENDATION MUST HAVE MEDIATION AND/OR OFFER CHILDREN
    // AND THAT IS A CRITERION TO MAKE THEM UNIQ
    let filteredRecommendations = recommendations.map(setUniqIdOnRecommendation)
    filteredRecommendations = filteredRecommendations.filter(
      recommendation => recommendation.uniqId
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.uniqId
    )

    // NOW WE CAN GIVE OTHER PROPERTIES TO THE GOOD SHAPED RECO
    filteredRecommendations = filteredRecommendations.map(
      (recommendation, index) => {
        const { mediation, offer } = recommendation
        const { product, venue } = offer || {}

        // FIXME Report the property computation on API side
        const firstThumbDominantColor =
          get(mediation, 'firstThumbDominantColor') ||
          get(product, 'firstThumbDominantColor')

        let distance
        if (!latitude || !longitude || !offer || !venue) {
          distance = '-'
        } else {
          const distanceInMeters = computeDistanceInMeters(
            latitude,
            longitude,
            venue.latitude,
            venue.longitude
          )
          distance = humanizeDistance(distanceInMeters)
        }

        // timezone
        const tz = getTimezone(get(venue, 'departementCode'))

        // return
        return Object.assign(
          {
            distance,
            firstThumbDominantColor,
            index,
            tz,
          },
          recommendation
        )
      }
    )

    return filteredRecommendations
  }
)

export default selectRecommendations
