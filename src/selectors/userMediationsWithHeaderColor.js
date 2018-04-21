import { createSelector } from 'reselect'

import selectUserMediationsWithIndex from './userMediationsWithIndex'
import getHeaderColor from '../getters/headerColor'
import getMediation from '../getters/mediation'
import getOffer from '../getters/offer'
import getSource from '../getters/source'

export default createSelector(selectUserMediationsWithIndex, userMediations =>
  userMediations.map((um, i) => {
    const mediation = getMediation(um)
    const offer = getOffer(um)
    const source = getSource(mediation, offer)
    const headerColor = getHeaderColor(mediation, source)
    return Object.assign(um, { headerColor })
  })
)
