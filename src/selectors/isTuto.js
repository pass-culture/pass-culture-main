import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectUserMediation from './userMediation'

export default createSelector(
  selectUserMediation,
  (userMediation) => {
    return userMediation && userMediation.userMediationOffers.length === 0 
  }
)
