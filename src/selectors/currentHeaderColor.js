import { rgb_to_hsv } from 'colorsys'
import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentMediationSelector from './currentMediation'
import currentEventOrThingSelector from './currentEventOrThing'
// import getHeaderColor from '../getters/headerColor'

export default createSelector(
  currentMediationSelector,
  currentEventOrThingSelector,
  (currentMediation, currentEventOrThing) => {
    const [red, green, blue] =
      get(currentMediation, 'firstThumbDominantColor') ||
      get(currentEventOrThing, 'firstThumbDominantColor') ||
      []
    const { h } = rgb_to_hsv(red, green, blue)
    if (h) {
      return `hsl(${h}, 100%, 7.5%)`
    }
    return 'black'
  }
)
