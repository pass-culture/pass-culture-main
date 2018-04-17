import get from 'lodash.get'
import { createSelector } from 'reselect'
import { rgb_to_hsv } from 'colorsys'

import { getMediation } from './mediation'
import { getOffer } from './offer'
import { getSource } from './source'
import selectUserMediationsWithIndex from './userMediationsWithIndex'

export function getHeaderColor (mediation, source) {
  const [red, green, blue] =
    get(mediation, 'firstThumbDominantColor') ||
    get(source, 'firstThumbDominantColor') || []
    const {h} = rgb_to_hsv(red, green, blue);
    if (h) {
      return `hsl(${h}, 100%, 7.5%)`;
    }
    return 'black';
}

export default createSelector(
  selectUserMediationsWithIndex,
  userMediations => userMediations.map((um, i) => {
    const mediation = getMediation(um)
    const offer = getOffer(um)
    const source = getSource(mediation, offer)
    const headerColor = getHeaderColor(mediation, source)
    return Object.assign(um, { headerColor })
  })
)
