import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'



function log (o) {
    console.log(o)
    return o
    }
export default createSelector(
  selectCurrentRecommendation,
  function (recommendation) { 
    const offers = get(recommendation, 'recommendationOffers', [])
    console.log("OFFERS", offers)
    const now = moment()
    return offers.every(o => moment(o.bookingLimitDatetime).isBefore(now)) // FIXME: also check that nbooking < available
  })
    
