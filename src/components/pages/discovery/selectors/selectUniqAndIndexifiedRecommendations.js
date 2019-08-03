import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { ROOT_PATH } from '../../../../utils/config'

export const fakeLastRecommendation = {
  discoveryIdentifier: 'tuto_-1',
  mediation: {
    firstThumbDominantColor: [205, 54, 70],
    frontText:
      'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.',
    id: 'fin',
    thumbCount: 1,
    tutoIndex: -1,
  },
  mediationId: 'fin',
  thumbUrl: `${ROOT_PATH}/splash-finReco@2x.png`
}

const selectUniqAndIndexifiedRecommendations = createSelector(
  state => state.data.recommendations,
  recommendations => {
    // RECOMMENDATION MUST HAVE MEDIATION AND/OR OFFER CHILDREN
    // AND THAT IS A CRITERION TO MAKE THEM UNIQ
    let filteredRecommendations = recommendations.filter(
      recommendation => recommendation.discoveryIdentifier
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.discoveryIdentifier
    )

    // NOW WE CAN GIVE OTHER PROPERTIES TO THE GOOD SHAPED RECO
    filteredRecommendations = filteredRecommendations.map(
      (recommendation, index) =>
        Object.assign(
          { index },
          recommendation
        ))

    filteredRecommendations.push(fakeLastRecommendation)

    return filteredRecommendations
  }
)

export default selectUniqAndIndexifiedRecommendations
