import { createSelector } from 'reselect'

import selectCurrentSource from './currentSource'
import selectCurrentOffer from './currentOffer'
import getVenue from '../getters/venue'
import getTimezone from '../getters/timezone'

export default createSelector(selectCurrentSource, selectCurrentOffer, getVenue, getTimezone)
