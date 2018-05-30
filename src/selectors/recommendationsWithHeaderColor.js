import { createSelector } from 'reselect'

import selectRecommendationsWithIndex from './recommendationsWithIndex'
import getHeaderColor from '../getters/headerColor'
import getMediation from '../getters/mediation'
import getOffer from '../getters/offer'
import getSource from '../getters/source'

export default createSelector(
  selectRecommendationsWithIndex,
  recommendations =>
    recommendations.map((um, i) => {
      const mediation = getMediation(um)
      const offer = getOffer(um)
      const source = getSource(mediation, offer)
      const headerColor = getHeaderColor(mediation, source)
      return Object.assign(um, { headerColor })
    })
)
