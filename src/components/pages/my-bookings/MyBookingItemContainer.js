/* eslint
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get'
import moment from 'moment'
import { capitalize } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { getTimezone } from '../../../utils/timezone'
import { selectRecommendation } from '../../../selectors'
import MyBookingItem from './MyBookingItem'

// TODO A tester
const getDateString = (date, tz) =>
  date &&
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY à H:mm')
  )

export const mapStateToProps = (state, ownProps) => {
  const { booking } = ownProps || {}
  const { isCancelled, recommendationId, stock, token } = booking
  const completedUrl = get(booking, 'completedUrl')
  const offerId = get(stock, 'resolvedOffer.id')
  const name = get(stock, 'resolvedOffer.product.name')
  const date = get(stock, 'beginningDatetime')
  const departementCode = get(stock, 'resolvedOffer.venue.departementCode')
  const timezone = getTimezone(departementCode)
  const dateString = getDateString(date, timezone)

  const recommendation = selectRecommendation(state, recommendationId)
  const mediationId = get(recommendation, 'mediationId')

  const isEvent = Boolean(get(stock, 'resolvedOffer.isEvent'))

  return {
    completedUrl,
    date,
    dateString,
    isCancelled,
    isEvent,
    mediationId,
    name,
    offerId,
    recommendation,
    timezone,
    token,
  }
}
export default connect(mapStateToProps)(MyBookingItem)
