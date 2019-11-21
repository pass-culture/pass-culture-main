import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { ROOT_PATH } from '../../../../utils/config'

export const fakeLastRecommendation = index => ({
  productOrTutoIdentifier: 'tuto_-1',
  index,
  mediation: {
    frontText:
      'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.',
    id: 'fin',
    thumbCount: 1,
    tutoIndex: -1,
  },
  mediationId: 'fin',
  thumbUrl: `${ROOT_PATH}/splash-finReco@2x.png`,
})

const selectUniqAndIndexifiedRecommendations = createSelector(
  state => state.data.recommendations,
  recommendations => {
    let filteredRecommendations = recommendations.filter(
      recommendation => recommendation.productOrTutoIdentifier
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.productOrTutoIdentifier
    )

    filteredRecommendations = filteredRecommendations.map((recommendation, index) =>
      Object.assign({ index }, recommendation)
    )

    filteredRecommendations.push(fakeLastRecommendation(filteredRecommendations.length))
    return filteredRecommendations
  }
)

export default selectUniqAndIndexifiedRecommendations
