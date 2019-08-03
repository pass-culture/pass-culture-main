import get from 'lodash.get'
import moment from 'moment'

const filterBookingsInLessThanTwoDays = (filtered, now = null) => {
  const nowMoment = now || moment()
  const twoDaysFromNow = nowMoment.clone().add(2, 'days')
  return filtered.filter(booking => {
    const date = get(booking, 'stock.beginningDatetime')
    const hasBeginningDatetime = Boolean(date)
    const isAfterNow = moment(date).isSameOrAfter(nowMoment)
    const isBeforeTwoDays = moment(date).isSameOrBefore(twoDaysFromNow)
    return hasBeginningDatetime && isBeforeTwoDays && isAfterNow
  })
}

export default filterBookingsInLessThanTwoDays
