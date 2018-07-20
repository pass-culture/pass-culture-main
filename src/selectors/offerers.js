import { createSelector } from 'reselect'

import {resolveDataCollection} from '../utils/resolvers'

export default createSelector(
  state => state.data.offerers,
  offerers => resolveDataCollection(offerers, 'offerers')
)
