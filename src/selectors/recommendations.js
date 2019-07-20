import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { humanizeRelativeDistance } from '../utils/geolocation'
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
    filteredRecommendations = filteredRecommendations.map((recommendation, index) => {
      const { mediation, offer } = recommendation
      const { product, venue } = offer || {}
      let distance = ''

      // FIXME Report the property computation on API side
      const firstThumbDominantColor =
        get(mediation, 'firstThumbDominantColor') || get(product, 'firstThumbDominantColor')

      // Les cartes tuto n'ont pas d'offre.
      if (offer) {
        distance = humanizeRelativeDistance(venue.latitude, venue.longitude, latitude, longitude)
      }

      const venueTimeZone = getTimezone(get(venue, 'departementCode'))

      return Object.assign(
        {
          distance,
          firstThumbDominantColor,
          index,
          tz: venueTimeZone,
        },
        recommendation
      )
    })

    return filteredRecommendations
  }
)

export default selectRecommendations
