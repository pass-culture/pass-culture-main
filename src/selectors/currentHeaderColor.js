import { createSelector } from 'reselect'
import get from 'lodash.get';
import { rgb_to_hsv } from 'colorsys'

import selectCurrentSource from './currentSource'
import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => selectCurrentSource(state),
  state => selectCurrentUserMediation(state),
  (currentSource, currentMediation) => {
    const [red, green, blue] =
      get(currentMediation, 'firstThumbDominantColor', []) ||
      get(currentSource, 'firstThumbDominantColor', [])
    const {h} = rgb_to_hsv(red, green, blue);
    if (h) {
      return `hsl(${h}, 100%, 15%)`;
    }
  }
)
