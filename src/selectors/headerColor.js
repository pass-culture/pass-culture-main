import { createSelector } from 'reselect'
import get from 'lodash.get';
import { rgb_to_hsv } from 'colorsys'

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => selectCurrentUserMediation(state),
  (currentUserMediation) => {
    const [red, green, blue] = get(currentUserMediation, 'thing.firstThumbDominantColor', []);
    const {h} = rgb_to_hsv(red, green, blue);
    return `hsl(${h}, 100%, 15%)`;
  }
)
