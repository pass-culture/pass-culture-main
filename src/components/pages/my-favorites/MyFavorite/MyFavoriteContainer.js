import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import track from 'react-tracking'

import Teaser from '../../../layout/Teaser/TeaserContainer'
import { isReserved, reservationStatus } from '../../../layout/Teaser/status'
import { formatRecommendationDates } from '../../../../utils/date/date'
import { getHumanizeRelativeDistance } from '../../../../utils/geolocation'
import getHumanizeRelativeDate from '../../../../utils/date/getHumanizeRelativeDate'
import { trackMatomoEventWrapper } from '../../../../helpers/matomoHelper'

import selectFirstMatchingBookingByOfferId from '../../../../selectors/selectFirstMatchingBookingByOfferId'
import selectOfferById from '../../../../selectors/selectOfferById'

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

export const mapDispatchToProps = (undefined, ownProps) => ({
  trackConsultOffer: offerId => {
    ownProps.tracking.trackEvent({ action: 'consultOffer', name: offerId })
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { trackConsultOffer } = dispatchProps
  const { favorite: { offerId } = {} } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackConsultOffer: () => trackConsultOffer(offerId),
  }
}

export default compose(
  withRouter,
  track({ page: 'Offer' }, { dispatch: trackMatomoEventWrapper }),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Teaser)
