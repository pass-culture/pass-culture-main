import get from 'lodash.get'
import { createSelector } from 'reselect'

import { API_URL, THUMBS_URL } from '../utils/config'

import createMediationsSelector from './createMediations'

export default (mediationsSelector=createMediationsSelector()) => createSelector(
  mediationsSelector,
  (state, event, thing) => event || thing,
  (mediations, eventOrthing) =>
    get(mediations, '0')
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : `${API_URL}${get(eventOrthing, 'thumbPath')}`
)
