import { createSelector } from 'reselect'

import selectCurrentMediation from './currentMediation'
import selectCurrentSource from './currentSource'
import getHeaderColor from '../getters/headerColor'

export default createSelector(
  selectCurrentSource,
  selectCurrentMediation,
  getHeaderColor
)
