import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import withTracking from '../../hocs/withTracking'
import Teaser from './Teaser'

import { isReserved, reservationStatuses } from './utils/statuses'
import { formatRecommendationDates } from '../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../utils/geolocation'
import selectFirstMatchingBookingByOfferId from '../../../selectors/selectFirstMatchingBookingByOfferId'
import selectOfferById from '../../../selectors/selectOfferById'
import getHumanizeRelativeDate from '../../../utils/date/getHumanizeRelativeDate'

export const mapStateToProps = (state, ownProps) => {
  const { item, handleToggleTeaser, isEditMode } = ownProps
  const { offerId, mediationId } = item
  const offer = selectOfferById(state, offerId)
  const { dateRange = [], isActive, isFinished, isFullyBooked, venue } = offer || {}
  const firstMatchingBooking = selectFirstMatchingBookingByOfferId(state, offerId)
  const isBooked = firstMatchingBooking ? !firstMatchingBooking.isCancelled : false
  const hasBookings = firstMatchingBooking !== null
  const offerBeginningDate = dateRange[0] || null
  const humanizeRelativeDate = offerBeginningDate
    ? getHumanizeRelativeDate(offerBeginningDate)
    : null
  const statuses = reservationStatuses(
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
  const date = isReserved(statuses)
    ? formatRecommendationDates(venue.departementCode, dateRange)
    : null

  return {
    date,
    detailsUrl,
    handleToggleTeaser,
    humanizeRelativeDistance,
    isEditMode,
    name: offer.name,
    offerId,
    offerTypeLabel: offer.offerType.appLabel,
    statuses,
    thumbUrl: item.thumbUrl,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { offerId } = stateProps
  return {
    ...stateProps,
    trackConsultOffer: () => {
      ownProps.tracking.trackEvent({ action: 'consultOffer', name: offerId })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(
    mapStateToProps,
    {},
    mergeProps
  )
)(Teaser)
