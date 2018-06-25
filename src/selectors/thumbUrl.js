import get from 'lodash.get'
import { createSelector } from 'reselect'

import { API_URL, THUMBS_URL } from '../utils/config'

import createMediationsSelector from './createMediations'

export default () => createSelector(
  createMediationsSelector(),
  (state, occasion) => occasion,
  (mediations, occasion) =>
    get(mediations, '0')
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : `${API_URL}${get(occasion, 'thumbPath')}`
)
