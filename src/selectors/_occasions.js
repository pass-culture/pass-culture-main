import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectEvents from './events'
import selectThings from './things'

export default createSelector(
  selectEvents,
  selectThings,
  (events, things) => {
    return [
      ...events,
      ...things
    ]
  }
)
