import moment from 'moment'
import get from 'lodash.get'
import { capitalize } from 'react-final-form-utils'
import { connect } from 'react-redux'

import { getTimezone } from '../../../utils/timezone'
import MyBooking from './MyBooking'
import { getQueryURL } from '../../../helpers'

const getDateString = (date, tz) =>
  date &&
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY à H:mm')
  )

const getLinkUrl = booking => {
  const mediationId = get(booking, 'recommendation.mediationId')
  const offerId = get(booking, 'stock.resolvedOffer.id')
  const queryURL = getQueryURL({ mediationId, offerId })
  return `/decouverte/${queryURL}/verso`
}

const getType = booking => {
  const isEvent = Boolean(get(booking, 'stock.resolvedOffer.isEvent'))
  return (isEvent && 'event') || 'thing'
}

const getBookingTimezone = booking => {
  const departementCode = get(
    booking,
    'stock.resolvedOffer.venue.departementCode'
  )
  return getTimezone(departementCode)
}

export const mapStateToProps = (state, ownProps) => {
  const { booking } = ownProps || {}
  const completedUrl = get(booking, 'completedUrl')
  const date = get(booking, 'stock.beginningDatetime')
  const timezone = getBookingTimezone(booking)
  const type = getType(booking)
  const dateString = getDateString(date, timezone)
  const isCancelled = get(booking, 'isCancelled')
  const linkURL = getLinkUrl(booking)
  const name = get(booking, 'stock.resolvedOffer.product.name')
  const thumbUrl = get(booking, 'recommendation.thumbUrl')
  const token = get(booking, 'token')

  let props = {
    completedUrl,
    date,
    isCancelled,
    linkURL,
    name,
    thumbUrl,
    timezone,
    token,
    type,
  }

  if (dateString) {
    props = {...props, dateString}
  }

  return props
}
export default connect(mapStateToProps)(MyBooking)
