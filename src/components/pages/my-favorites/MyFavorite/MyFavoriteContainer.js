import { connect } from 'react-redux'

import MyFavorite from './MyFavorite'
import { humanizeRelativeDate } from '../../../../utils/date/date'
import { humanizeRelativeDistance } from '../../../../utils/geolocation'
import { versoUrl } from '../../../../utils/url/url'

export const hasBookings = offer => offer.stocks.some(stock => stock.bookings.length > 0)

export const isBooked = offer => {
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
  humanizeRelativeDate = ''
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
  const { mediation, offer } = favorite
  const { latitude, longitude } = state.geolocation
  const offerBeginningDate = offer.dateRange[0] || null
  const {
    product: {
      offerType: { appLabel = '' },
    },
  } = offer

  return {
    humanizeRelativeDistance: humanizeRelativeDistance(
      offer.venue.latitude,
      offer.venue.longitude,
      latitude,
      longitude
    ),
    name: offer.name,
    offerTypeLabel: appLabel,
    status: reservationStatus(
      offer.isFinished,
      offer.isFullyBooked,
      hasBookings(offer),
      isBooked(offer),
      offerBeginningDate ? humanizeRelativeDate(offerBeginningDate) : null
    ),
    thumbUrl: mediation.thumbUrl,
    versoUrl: versoUrl(favorite.offerId, favorite.mediationId),
  }
}

export default connect(mapStateToProps)(MyFavorite)
