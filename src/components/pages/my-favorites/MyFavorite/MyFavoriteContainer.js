import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import MyFavorite from './MyFavorite'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import selectFirstMatchingBookingByStocks from '../../../../selectors/selectFirstMatchingBookingByStocks'
import selectOfferById from '../../../../selectors/selectOfferById'
import getHumanizeRelativeDate from '../../../../utils/date/getHumanizeRelativeDate'

export const reservationStatus = (
  isFinished,
  isFullyBooked,
  hasBookings,
  isBooked,
  humanizeRelativeDate
) => {
  if (isFinished) {
    return {
      label: 'Terminé',
      class: 'finished',
    }
  } else if (isFullyBooked) {
    return {
      label: 'Épuisé',
      class: 'fully-booked',
    }
  } else if (hasBookings) {
    if (isBooked) {
      return {
        label: 'Réservé',
        class: 'booked',
      }
    } else {
      return {
        label: 'Annulé',
        class: 'cancelled',
      }
    }
  } else if (humanizeRelativeDate) {
    if (humanizeRelativeDate === 'Demain') {
      return {
        label: humanizeRelativeDate,
        class: 'tomorrow',
      }
    } else {
      return {
        label: humanizeRelativeDate,
        class: 'today',
      }
    }
  }

  return null
}

export const mapStateToProps = (state, ownProps) => {
  const { favorite } = ownProps
  const { offerId } = favorite
  const offer = selectOfferById(state, offerId)
  const { venue } = offer
  const firstMatchingBooking = selectFirstMatchingBookingByStocks(state)
  const isBooked = firstMatchingBooking ? !firstMatchingBooking.isCancelled : false
  const hasBookings = typeof firstMatchingBooking !== 'undefined'
  const { dateRange = [], isFinished, isFullyBooked } = offer || {}
  const offerBeginningDate = dateRange[0] || null
  const humanizeRelativeDate = offerBeginningDate
    ? getHumanizeRelativeDate(offerBeginningDate)
    : null
  const status = reservationStatus(
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

  return {
    detailsUrl,
    humanizeRelativeDistance,
    offer,
    status,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyFavorite)
