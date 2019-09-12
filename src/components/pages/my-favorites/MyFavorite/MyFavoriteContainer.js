import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Teaser from '../../../layout/Teaser/TeaserContainer'
import { formatRecommendationDates } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import { isReserved, reservationStatus } from '../../../layout/Teaser/status'
import selectFirstMatchingBookingByOfferId from '../../../../selectors/selectFirstMatchingBookingByOfferId'
import selectOfferById from '../../../../selectors/selectOfferById'
import getHumanizeRelativeDate from '../../../../utils/date/getHumanizeRelativeDate'

export const mapStateToProps = (state, ownProps) => {
  const { favorite, handleToggleItem, isEditMode } = ownProps
  const { offerId, mediationId } = favorite
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
  const stringifiedMediationId = mediationId ? `/${mediationId}` : ''
  const detailsUrl = `${pathname}/details/${offer.id}${stringifiedMediationId}${search}`
  const date = isReserved(status)
    ? formatRecommendationDates(venue.departementCode, dateRange)
    : null

  return {
    date,
    detailsUrl,
    handleToggleItem,
    humanizeRelativeDistance,
    isEditMode,
    name: offer.name,
    offerId,
    offerTypeLabel: offer.offerType.appLabel,
    status,
    thumbUrl: favorite.thumbUrl,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Teaser)
