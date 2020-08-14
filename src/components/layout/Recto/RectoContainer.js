import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { DEFAULT_THUMB_URL } from '../../../utils/thumb'
import Recto from './Recto'
import { selectMediationByOfferId } from '../../../redux/selectors/data/mediationsSelectors'
import { selectThumbUrlByRouterMatch } from '../../../redux/selectors/data/thumbUrlSelector'
import { selectBookingById } from '../../../redux/selectors/data/bookingsSelectors'
import { selectStockById } from '../../../redux/selectors/data/stocksSelectors'
import { selectOfferById } from '../../../redux/selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match, recommendation } = ownProps
  const { params } = match
  const { bookingId, offerId } = params

  if (bookingId) {
    return findThumbByBookingId(state, bookingId)
  } else {
    return findThumbByOfferId(state, offerId, match, recommendation)
  }
}

export const findThumbByBookingId = (state, bookingId) => {
  let thumbUrl = ''
  let withMediation = false

  const booking = selectBookingById(state, bookingId)
  const { stockId = '' } = booking
  const stock = selectStockById(state, stockId)
  const { offerId = '' } = stock || {}
  const mediation = selectMediationByOfferId(state, offerId)
  const offer = selectOfferById(state, offerId)

  if (mediation) {
    withMediation = true
  }
  thumbUrl = offer.thumbUrl ? offer.thumbUrl : DEFAULT_THUMB_URL

  return {
    thumbUrl,
    withMediation,
  }
}

export const findThumbByOfferId = (state, offerId, match, recommendation) => {
  let thumbUrl = ''
  let withMediation = false

  const mediation = selectMediationByOfferId(state, offerId)
  if (!mediation) {
    thumbUrl = selectThumbUrlByRouterMatch(state, match)
  } else {
    thumbUrl = recommendation ? recommendation.thumbUrl : mediation.thumbUrl
    withMediation = true
  }

  return {
    thumbUrl,
    withMediation,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Recto)
