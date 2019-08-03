import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import MyFavorite from './MyFavorite'

import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import selectOfferById from '../../../../selectors/selectOfferById'
import getHumanizeRelativeDate from '../../../../utils/date/getHumanizeRelativeDate'

export const getHasBookings = offer => offer.stocks.some(stock => stock.bookings.length > 0)

export const getIsBooked = offer => {
  let flag = false

  offer.stocks.forEach(stock => {
    const { bookings } = stock
    const hasAtLeastOneBooking = bookings.length > 0

    if (hasAtLeastOneBooking) {
      const lastBooking = bookings.slice(-1)[0]

      if (!lastBooking.isCancelled) {
        flag = true
      }
    }
  })

  return flag
}

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
  const isBooked = getIsBooked(offer)
  const hasBookings = getHasBookings(offer)
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
  return {
    humanizeRelativeDistance,
    offer,
    status,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyFavorite)
