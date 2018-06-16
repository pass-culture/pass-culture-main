import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import getOccurences from '../getters/occurences'

export default () => createSelector(
  state => state.data.eventOccurences,
  (state, ownProps) => get(ownProps, 'occasion.id'),
  getOccurences
)
