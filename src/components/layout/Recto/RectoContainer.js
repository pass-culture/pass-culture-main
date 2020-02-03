import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { DEFAULT_THUMB_URL } from '../../../utils/thumb'
import Recto from './Recto'
import { selectMediationByOfferId } from '../../../selectors/data/mediationsSelectors'
import { selectThumbUrlByRouterMatch } from '../../../selectors/data/thumbUrlSelector'
import { selectBookingById } from '../../../selectors/data/bookingsSelectors'
import { selectStockById } from '../../../selectors/data/stocksSelectors'

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
  let frontText = ''
  let thumbUrl = ''
  let withMediation = false

  if (bookingId !== 'menu') {
    const booking = selectBookingById(state, bookingId)
    const { stockId = '' } = booking
    const stock = selectStockById(state, stockId)
    const { offerId = '' } = stock || {}
    const mediation = selectMediationByOfferId(state, offerId)

    if (mediation) {
      frontText = mediation.frontText
      withMediation = true
    }
    thumbUrl = booking.thumbUrl ? booking.thumbUrl : DEFAULT_THUMB_URL
  }

  return {
    frontText,
    thumbUrl,
    withMediation
  }
}

export const findThumbByOfferId = (state, offerId, match, recommendation) => {
  let frontText = ''
  let thumbUrl = ''
  let withMediation = false

  const mediation = selectMediationByOfferId(state, offerId)
  if (!mediation) {
    thumbUrl = selectThumbUrlByRouterMatch(state, match)
  } else {
    frontText = mediation.frontText
    thumbUrl = recommendation ? recommendation.thumbUrl : mediation.thumbUrl
    withMediation = true
  }

  return {
    frontText,
    thumbUrl,
    withMediation
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Recto)
