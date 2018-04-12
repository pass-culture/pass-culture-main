import { createSelector } from 'reselect'
import get from 'lodash.get';
import { rgb_to_hsv } from 'colorsys'

import selectSource from './source'
import selectMediation from './mediation'

export default createSelector(
  selectSource,
  selectMediation,
  (source, mediation) => {
    const firstThumbDominantColor = get(mediation, 'firstThumbDominantColor', []) ||
      get(source, 'firstThumbDominantColor', [])
    if (!firstThumbDominantColor) {
      return
    }
    const [red, green, blue] = firstThumbDominantColor
    const {h} = rgb_to_hsv(red, green, blue);
    if (h) {
      return `hsl(${h}, 100%, 7.5%)`;
    }
    return 'black';
  }
)
