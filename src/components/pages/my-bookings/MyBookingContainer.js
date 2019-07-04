import moment from 'moment'
import { capitalize } from 'react-final-form-utils'
import { connect } from 'react-redux'

import MyBooking from './MyBooking'
import { getTimezone } from '../../../utils/timezone'

export const stringify = date => timeZone =>
  capitalize(
    moment(date)
      .tz(timeZone)
      .format('dddd DD/MM/YYYY à H:mm')
  )

export const updatePropsWithDateElements = (
  props,
  beginningDateTime,
  departementCode
) => {
  const timeZone = getTimezone(departementCode)
  const stringifyDate = stringify(beginningDateTime)(timeZone)

  return { ...props, stringifyDate }
}

export const urlOf = myBooking => {
  const urlElements = [
    '',
    'decouverte',
    myBooking.stock.resolvedOffer.id,
    'verso',
  ]
  if (myBooking.recommendation.mediationId) {
    urlElements.splice(
      3,
      0,
      myBooking.recommendation.mediationId
    )
  }

  return urlElements.join('/')
}

export const mapStateToProps = (state, ownProps) => {
  const { booking } = ownProps
  const beginningDateTime = booking.stock.beginningDatetime

  let props = {
    isCancelled: booking.isCancelled,
    name: booking.stock.resolvedOffer.product.name,
    offerVersoUrl: urlOf(booking),
    thumbUrl: booking.recommendation.thumbUrl,
    token: booking.token.toLowerCase(),
  }

  if (beginningDateTime) {
    props = updatePropsWithDateElements(
      props,
      beginningDateTime,
      booking.stock.resolvedOffer.venue.departementCode
    )
  }

  return props
}

export default connect(mapStateToProps)(MyBooking)
