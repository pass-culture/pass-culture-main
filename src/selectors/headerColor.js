import { createSelector } from 'reselect'
import get from 'lodash.get';
import { rgb_to_hsv } from 'colorsys'

import selectSource from './source'
import selectUserMediation from './userMediation'

export default createSelector(
  selectSource,
  selectUserMediation,
  (source, mediation) => {
    const [red, green, blue] =
      get(mediation, 'firstThumbDominantColor', []) ||
      get(source, 'firstThumbDominantColor', [])
    const {h} = rgb_to_hsv(red, green, blue);
    if (h) {
      return `hsl(${h}, 100%, 15%)`;
    }
  }
)
