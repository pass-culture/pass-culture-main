import { createSelector } from 'reselect'

import selectCurrentVenue from './currentVenue'
import getTimezone from '../getters/timezone'

export default createSelector(selectCurrentVenue, getTimezone)
