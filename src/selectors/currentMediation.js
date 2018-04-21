import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'
import getMediation from '../getters/mediation'

export default createSelector(selectCurrentRecommendation, getMediation)
