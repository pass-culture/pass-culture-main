import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import withTracking from '../../hocs/withTracking'
import Teaser from './Teaser'
import { isReserved, reservationStatuses } from './utils/statuses'
import { formatRecommendationDates } from '../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../utils/geolocation'
import getHumanizeRelativeDate from '../../../utils/date/getHumanizeRelativeDate'
import getIsBooked from '../../../utils/getIsBooked'
import { getTimezoneFromOffer } from '../../../utils/timezone'
import { selectOfferById } from '../../../redux/selectors/data/offersSelectors'
import { selectStockById } from '../../../redux/selectors/data/stocksSelectors'
import { selectFirstMatchingBookingByOfferId } from '../../../redux/selectors/data/bookingsSelectors'
import { selectSearchGroup } from '../../../redux/selectors/data/categoriesSelectors'

export const humanizeBeginningDateTime = (hasBookings, state, booking) => {
  let humanizeRelativeDate = ''

  if (hasBookings) {
    const stock = selectStockById(state, booking.stockId)
    const { offerId } = stock
    const offer = selectOfferById(state, offerId)
    const timezone = getTimezoneFromOffer(offer)
    humanizeRelativeDate = getHumanizeRelativeDate(stock.beginningDatetime, timezone)
  }

  return humanizeRelativeDate
}

export const mapStateToProps = (state, ownProps) => {
  const { handleToggleTeaser, favorite, isEditMode, match } = ownProps
  const { offerId, mediationId } = favorite
  const offer = selectOfferById(state, offerId)
  const { dateRange, isActive, hasBookingLimitDatetimesPassed, venue } = offer
  const booking = selectFirstMatchingBookingByOfferId(state, offerId)
  const isBooked = getIsBooked(booking)
  const hasBookings = booking !== null
  const humanizeRelativeDistance = getHumanizeRelativeDistance(
    state.geolocation.latitude,
    state.geolocation.longitude,
    venue.latitude,
    venue.longitude
  )
  const { search } = location
  const stringifiedMediationId = mediationId ? `/${mediationId}` : '/vide'
  const detailsUrl = `${match.path}/details/${offer.id}${stringifiedMediationId}${search}`
  const humanizeRelativeDate = humanizeBeginningDateTime(hasBookings, state, booking)
  const statuses = reservationStatuses(
    isActive,
    hasBookingLimitDatetimesPassed,
    hasBookings,
    humanizeRelativeDate,
    isBooked
  )
  const date = isReserved(statuses)
    ? formatRecommendationDates(venue.departementCode, dateRange)
    : null
  const searchGroup = selectSearchGroup(state, offer)

  return {
    date,
    detailsUrl,
    handleToggleTeaser,
    humanizeRelativeDistance,
    isEditMode,
    name: offer.name,
    offerId,
    searchGroupLabel: searchGroup.value,
    statuses,
    thumbUrl: favorite.thumbUrl,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { offerId } = stateProps
  return {
    ...stateProps,
    trackConsultOffer: () => {
      ownProps.tracking.trackEvent({ action: 'ConsultOffer_FromFavorite', name: offerId })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(mapStateToProps, {}, mergeProps)
)(Teaser)
