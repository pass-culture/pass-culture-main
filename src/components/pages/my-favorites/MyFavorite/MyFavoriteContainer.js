import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import MyFavorite from './MyFavorite'
import { formatRecommendationDates } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import selectFirstMatchingBookingByOfferId from '../../../../selectors/selectFirstMatchingBookingByOfferId'
import selectOfferById from '../../../../selectors/selectOfferById'
import getHumanizeRelativeDate from '../../../../utils/date/getHumanizeRelativeDate'

export const isReserved = status =>
  !(status.length > 0 && status[0].class.match('cancelled|finished|fully-booked'))

export const reservationStatus = (
  isActive,
  isFinished,
  isFullyBooked,
  hasBookings,
  isBooked,
  humanizeRelativeDate
) => {
  const status = []

  if (isFinished) {
    return [
      {
        label: 'Terminé',
        class: 'finished',
      },
    ]
  }

  if (!isActive || (hasBookings && !isBooked)) {
    return [
      {
        label: 'Annulé',
        class: 'cancelled',
      },
    ]
  }

  if (isFullyBooked) {
    return [
      {
        label: 'Épuisé',
        class: 'fully-booked',
      },
    ]
  }

  if (hasBookings && isBooked) {
    status.push({
      label: 'Réservé',
      class: 'booked',
    })
  }

  if (humanizeRelativeDate) {
    if (humanizeRelativeDate === 'Demain') {
      status.push({
        label: humanizeRelativeDate,
        class: 'tomorrow',
      })
    } else {
      status.push({
        label: humanizeRelativeDate,
        class: 'today',
      })
    }
  }

  return status
}

export const mapStateToProps = (state, ownProps) => {
  const { favorite } = ownProps
  const { offerId } = favorite
  const offer = selectOfferById(state, offerId)
  const { dateRange = [], isActive, isFinished, isFullyBooked, venue } = offer || {}
  const firstMatchingBooking = selectFirstMatchingBookingByOfferId(state, offerId)
  const isBooked = firstMatchingBooking ? !firstMatchingBooking.isCancelled : false
  const hasBookings = firstMatchingBooking !== null
  const offerBeginningDate = dateRange[0] || null
  const humanizeRelativeDate = offerBeginningDate
    ? getHumanizeRelativeDate(offerBeginningDate)
    : null
  const status = reservationStatus(
    isActive,
    isFinished,
    isFullyBooked,
    hasBookings,
    isBooked,
    humanizeRelativeDate
  )
  const humanizeRelativeDistance = getHumanizeRelativeDistance(
    state.geolocation.latitude,
    state.geolocation.longitude,
    venue.latitude,
    venue.longitude
  )
  const { pathname, search } = location
  const mediationId = favorite.mediationId ? `/${favorite.mediationId}` : ''
  const detailsUrl = `${pathname}/details/${offer.id}${mediationId}${search}`
  const date = isReserved(status)
    ? formatRecommendationDates(venue.departementCode, dateRange)
    : null

  return {
    date,
    detailsUrl,
    humanizeRelativeDistance,
    name: offer.name,
    offerTypeLabel: offer.product.offerType.appLabel,
    status,
    thumbUrl: favorite.thumbUrl,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyFavorite)
